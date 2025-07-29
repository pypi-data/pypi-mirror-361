# Copyright 2025 DeepMind Technologies Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Wraps the Ollama API into a Processor.

This module allows grounding Processor pipelines with locally-run LLMs, such as
Gemma. To use the module, you must install Ollama. You can find the full
instructions at https://ai.google.dev/gemma/docs/integrations/ollama. Also
before working with Gemma models, make sure you have requested access via Kaggle
[https://ai.google.dev/gemma/docs/setup#get-access] and reviewed the Gemma terms
of use [https://ai.google.dev/gemma/terms].

```sh
# Install Ollama itself.
curl -fsSL https://ollama.com/install.sh | sh
# Pull the Gemma model.
ollama pull gemma3
```
"""

import base64
from collections.abc import AsyncIterable
import json
from typing import Any, Literal
from genai_processors import content_api
from genai_processors import mime_types
from genai_processors import processor
from google.genai import _transformers
from google.genai import types as genai_types
import httpx
from pydantic import json_schema
from typing_extensions import TypedDict


_DEFAULT_HOST = 'http://127.0.0.1:11434'
# Ollama connection timeout. It may take some time for Ollama to load the model.
_DEFAULT_TIMEOUT = 300


class GenerateContentConfig(TypedDict, total=False):
  """Optional model configuration parameters."""

  system_instruction: content_api.ProcessorContentTypes
  """Instructions for the model to steer it toward better performance.

  For example, "Answer as concisely as possible" or "Don't use technical
  terms in your response".
  """

  response_mime_type: (
      Literal['text/plain', 'application/json', 'text/x.enum'] | None
  )
  """Output response mimetype of the generated candidate text."""

  response_schema: genai_types.SchemaUnion | None = None
  """The `Schema` object allows the definition of input and output data types.

  These types can be objects, but also primitives and arrays.
  Represents a select subset of an [OpenAPI 3.0 schema
  object](https://spec.openapis.org/oas/v3.0.3#schema).
  If set, a compatible response_mime_type must also be set.
  Compatible mimetypes: `application/json`: Schema for JSON response.
  """

  response_json_schema: json_schema.JsonSchemaValue | None
  """Output schema of the generated response.

  This is an alternative to `response_schema` that accepts [JSON
  Schema](https://json-schema.org/). If set, `response_schema` must be
  omitted, but `response_mime_type` is required. While the full JSON Schema
  may be sent, not all features are supported.
  """

  seed: int | None
  """Seed."""

  stop_sequences: list[str]
  """Stop sequences."""

  temperature: float | None
  """Controls the randomness of predictions."""

  top_k: float | None
  """If specified, top-k sampling will be used."""

  top_p: float | None
  """If specified, nucleus sampling will be used."""

  tools: list[genai_types.Tool] | None
  """Tools the model may call."""


class OllamaModel(processor.Processor):
  """`Processor` that calls the Ollama in turn-based fashion.

  Note: All content is buffered prior to calling Ollama.
  """

  def __init__(
      self,
      *,
      model_name: str = '',
      host: str | None = None,
      generate_content_config: GenerateContentConfig | None = None,
      keep_alive: float | str | None = None,
  ):
    """Initializes the Ollama model.

    Args:
      model_name: Name of the model to use e.g. gemma3.
      host: Model server address.
      generate_content_config: Inference settings.
      keep_alive: Instructs server how long to keep the model loaded. Can be:
        * A duration string (such as "10m" or "24h")
        * A number in seconds
        * A negative number to keep the model loaded in memory
        * 0 to unload it immediately after generating a response

    Returns:
      A `Processor` that calls the Ollama API in turn-based fashion.
    """  # fmt: skip
    generate_content_config = generate_content_config or {}

    self._host = host or _DEFAULT_HOST
    self._model_name = model_name
    self._format = None
    self._strip_quotes = False
    self._keep_alive = keep_alive

    if tools := generate_content_config.get('tools'):
      self._tools = []
      for tool in tools:
        for tool_name in (
            'retrieval',
            'google_search',
            'google_search_retrieval',
            'enterprise_web_search',
            'google_maps',
            'url_context',
            'code_execution',
            'computer_use',
        ):
          if getattr(tool, tool_name) is not None:
            raise ValueError(f'Tool {tool_name} is not supported.')

        for fdecl in tool.function_declarations or ():
          if fdecl.parameters:
            parameters = _transformers.t_schema(  # pytype: disable=wrong-arg-types
                _FakeClient(), fdecl.parameters
            ).json_schema.model_dump(
                mode='json', exclude_unset=True
            )
          else:
            parameters = None

          self._tools.append({
              'type': 'function',
              'function': {
                  'name': fdecl.name,
                  'description': fdecl.description,
                  'parameters': parameters,
              },
          })
    else:
      self._tools = None

    self._client = httpx.AsyncClient(
        follow_redirects=True,
        headers={
            'Content-Type': mime_types.TEXT_JSON,
            'Accept': mime_types.TEXT_JSON,
            'User-Agent': 'genai-processors',
        },
        timeout=_DEFAULT_TIMEOUT,
    )

    response_mime_type = generate_content_config.get('response_mime_type')
    if response_mime_type == mime_types.TEXT_JSON:
      self._format = 'json'
    elif response_mime_type == mime_types.TEXT_ENUM:
      # Ollama only supports JSON schema constrained decoding. So for enum names
      # it will return strings enclosed in quotes.
      self._strip_quotes = True

    # Render response_schema in-to a JSON schema.
    if generate_content_config.get('response_schema') is not None:
      self._format = _transformers.t_schema(  # pytype: disable=wrong-arg-types
          _FakeClient(), generate_content_config['response_schema']
      ).json_schema.model_dump(mode='json', exclude_unset=True)
    elif generate_content_config.get('response_json_schema'):
      self._format = generate_content_config['response_json_schema']

    # Populate system instructions.
    self._system_instruction = []
    for part in content_api.ProcessorContent(
        generate_content_config.get('system_instruction', ())
    ):
      self._system_instruction.append(
          _to_ollama_message(part, default_role='system')
      )

    self._options = {}
    for field in ('seed', 'temperature', 'top_k', 'top_p'):
      if generate_content_config.get(field) is not None:
        self._options[field] = generate_content_config[field]
    if generate_content_config.get('stop_sequences'):
      self._options['stop'] = generate_content_config['stop_sequences']

  async def call(
      self, content: AsyncIterable[content_api.ProcessorPartTypes]
  ) -> AsyncIterable[content_api.ProcessorPartTypes]:
    messages = []
    async for part in content:
      messages.append(_to_ollama_message(part, default_role='user'))
    if not messages:
      return

    request = dict(
        model=self._model_name,
        messages=self._system_instruction + messages,
        tools=self._tools,
        format=self._format,
        options=self._options,
        keep_alive=self._keep_alive,
    )

    async with self._client.stream(
        'POST', self._host + '/api/chat', json=request
    ) as r:
      try:
        r.raise_for_status()
      except httpx.HTTPStatusError as e:
        await r.aread()
        raise httpx.HTTPStatusError(
            f'{e}: {r.json()["error"]}', request=e.request, response=e.response
        )

      async for line in r.aiter_lines():
        part = json.loads(line)
        if err := part.get('error'):
          raise RuntimeError(err)
        message = part['message']

        if message.get('content'):
          if self._strip_quotes:
            message['content'] = message['content'].replace('"', '')
          yield content_api.ProcessorPart(
              message['content'], role=message['role'].upper()
          )
        if tool_calls := message.get('tool_calls'):
          for tool_call in tool_calls:
            yield processor.ProcessorPart.from_function_call(
                name=tool_call['function']['name'],
                args=tool_call['function']['arguments'],
            )
        for image in message.get('images', ()):
          yield content_api.ProcessorPart(
              image, mimetype='image/*', role=message.role.upper()
          )


def _to_ollama_message(
    part: content_api.ProcessorPart, default_role: str = ''
) -> dict[str, Any]:
  """Returns Ollama message JSON."""
  # Gemini API uses upper case for roles, while Ollama uses lower case.
  message: dict[str, Any] = {'role': part.role.lower() or default_role.lower()}

  if part.function_call:
    message.setdefault('tool_calls', []).append({
        'name': part.function_call.name,
        'arguments': part.function_call.args,
    })
    return message
  elif part.function_response:
    message['role'] = 'tool'
    message['content'] = json.dumps(part.function_response.response)
    message['name']: part.function_response.name
    return message
  elif content_api.is_text(part.mimetype):
    message['content'] = part.text
  elif content_api.is_image(part.mimetype):
    message['images'] = [base64.b64encode(part.bytes).decode('utf8')]
  else:
    raise ValueError(f'Unsupported Part type: {part.mimetype}')

  return message


class _FakeClient:
  """A fake genai client to invoke t_schema."""

  def __init__(self):
    self.vertexai = False
