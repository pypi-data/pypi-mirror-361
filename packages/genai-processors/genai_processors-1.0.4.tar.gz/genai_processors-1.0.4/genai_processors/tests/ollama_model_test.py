import enum
import http
import json
import unittest
from unittest import mock

from absl.testing import parameterized
from genai_processors import content_api
from genai_processors import processor
from genai_processors.core import ollama_model
from google.genai import types as genai_types
import httpx


class OkEnum(enum.StrEnum):
  OK = 'OK'
  OKAY = 'okay'


class OllamaProcessorTest(parameterized.TestCase):

  def test_inference(self):
    def request_handler(request: httpx.Request):
      self.assertEqual(str(request.url), 'http://127.0.0.1:11434/api/chat')
      self.assertEqual(
          json.loads(request.content.decode('utf-8')),
          {
              'model': 'gemma3',
              'messages': [
                  {
                      'role': 'system',
                      'content': 'You are an OK agent: you respond with OK.',
                  },
                  {'role': 'user', 'images': ['UE5HRw0KGgo=']},
                  {'role': 'user', 'content': 'is this image okay?'},
              ],
              'tools': None,
              'format': {
                  'type': 'string',
                  'title': 'OkEnum',
                  'enum': ['OK', 'okay'],
              },
              'options': {},
              'keep_alive': None,
          },
      )

      response = (
          '{"message": {"content": "O", "role": "model"}}\n'
          '{"message": {"content": "K", "role": "model"}}\n'
      )
      return httpx.Response(
          http.HTTPStatus.OK, content=response.encode('utf-8')
      )

    mock_client = httpx.AsyncClient(
        transport=httpx.MockTransport(request_handler)
    )

    with mock.patch.object(httpx, 'AsyncClient', return_value=mock_client):
      model = ollama_model.OllamaModel(
          model_name='gemma3',
          generate_content_config=ollama_model.GenerateContentConfig(
              system_instruction='You are an OK agent: you respond with OK.',
              response_schema=OkEnum,
              response_mime_type='text/x.enum',
          ),
      )
      output = processor.apply_sync(
          model,
          [
              content_api.ProcessorPart(
                  b'PNG\x47\x0D\x0A\x1A\x0A', mimetype='image/png'
              ),
              'is this image okay?',
          ],
      )

    self.assertEqual(content_api.as_text(output), 'OK')

  def test_inference_with_tool(self):
    def request_handler(request: httpx.Request):
      json_body = json.loads(request.content.decode('utf-8'))
      self.assertEqual(
          json_body['tools'],
          [{
              'type': 'function',
              'function': {
                  'name': 'get_weather',
                  'description': 'Get the current weather',
                  'parameters': {
                      'properties': {
                          'location': {
                              'type': 'string',
                              'description': (
                                  'The city and state, e.g. San Francisco, CA'
                              ),
                          }
                      },
                      'type': 'object',
                      'required': ['location'],
                  },
              },
          }],
      )

      if len(json_body['messages']) == 1:
        response = {
            'message': {
                'role': 'model',
                'content': '',
                'tool_calls': [{
                    'function': {
                        'name': 'get_weather',
                        'arguments': {'location': 'Boston, MA'},
                    }
                }],
            }
        }
      else:
        response = {
            'message': {
                'role': 'assistant',
                'content': 'The weather in Boston is 72 and sunny.',
            }
        }

      return httpx.Response(
          http.HTTPStatus.OK, content=json.dumps(response).encode('utf-8')
      )

    mock_client = httpx.AsyncClient(
        transport=httpx.MockTransport(request_handler)
    )

    with mock.patch.object(httpx, 'AsyncClient', return_value=mock_client):
      weather_tool = genai_types.Tool(
          function_declarations=[
              genai_types.FunctionDeclaration(
                  name='get_weather',
                  description='Get the current weather',
                  parameters=genai_types.Schema(
                      type=genai_types.Type.OBJECT,
                      properties={
                          'location': genai_types.Schema(
                              type=genai_types.Type.STRING,
                              description=(
                                  'The city and state, e.g. San Francisco, CA'
                              ),
                          )
                      },
                      required=['location'],
                  ),
              )
          ]
      )
      model = ollama_model.OllamaModel(
          model_name='gemma3',
          generate_content_config=ollama_model.GenerateContentConfig(
              tools=[weather_tool]
          ),
      )

      conversation = ['What is the weather in Boston?']

      output = processor.apply_sync(model, conversation)
      self.assertEqual(len(output), 1)  # pylint: disable=g-generic-assert
      self.assertEqual(
          output[0],
          content_api.ProcessorPart.from_function_call(
              name='get_weather', args={'location': 'Boston, MA'}
          ),
      )
      conversation.extend(output)

      conversation.append(
          content_api.ProcessorPart.from_function_response(
              name='get_weather',
              response={'weather': '72 and sunny'},
          )
      )
      output = processor.apply_sync(model, conversation)

      self.assertEqual(
          content_api.as_text(output), 'The weather in Boston is 72 and sunny.'
      )


if __name__ == '__main__':
  unittest.main()
