import asyncio
from collections.abc import AsyncIterable
import traceback
from typing import Sequence, cast
import unittest

from absl.testing import parameterized
from genai_processors import content_api
from genai_processors import mime_types
from genai_processors import processor
from genai_processors import streams
from google.genai import types as genai_types


def get_processor_parts(
    str_list: Sequence[str],
) -> list[content_api.ProcessorPart]:
  content_chunk = []
  for s in str_list:
    content_chunk.append(content_api.ProcessorPart(s))
  return content_chunk


@processor.processor_function
async def _check_is_part(
    content: AsyncIterable[content_api.ProcessorPart],
) -> AsyncIterable[content_api.ProcessorPart]:
  async for part in content:
    if not isinstance(part, content_api.ProcessorPart):
      raise ValueError(f'{part!r} is not a content_api.ProcessorPart.')
    yield part


class ProcessorPipelineTest(unittest.TestCase):

  def test_sets_debug_substream_name(self):
    result = processor.debug('text')
    for part in content_api.ProcessorContent(result):
      self.assertEqual(part.substream_name, 'debug')

  def test_sets_status_substream_name(self):
    result = processor.status('text')
    for part in content_api.ProcessorContent(result):
      self.assertEqual(part.substream_name, 'status')

  def test_chain_processors(self):
    @processor.processor_function
    async def processor_0(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for c in content:
        yield processor.debug('test')
        yield c

    @processor.processor_function
    async def processor_1(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for c in content:
        await asyncio.sleep(1)
        yield c

    combined_processor = processor_0 + processor_1

    input_stream = get_processor_parts(['foo', 'bar'])
    output = processor.apply_sync(combined_processor, input_stream)
    output = [output.text for output in output]
    self.assertEqual(output, ['test', 'foo', 'test', 'bar'])

  def test_applies_async(self):
    inputs = get_processor_parts(['0', '1', '2'])

    @processor.processor_function
    async def slow_noop(
        inputs: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for x in inputs:
        await asyncio.sleep(1)
        yield x

    processed = processor.apply_sync(slow_noop, inputs)
    self.assertEqual(processed, inputs)

  def test_chained_processor_raises_yielded_exception(self):
    err_msg = 'bar is bad'

    @processor.processor_function
    async def processor_0(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for c in content:
        if c.text == 'bar':
          raise ValueError(err_msg)
        yield c

    @processor.processor_function
    async def processor_1(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for c in content:
        await asyncio.sleep(1)
        yield c

    combined_processor = processor_0 + processor_1

    with self.assertRaisesRegex(ValueError, err_msg):
      _ = processor.apply_sync(
          combined_processor,
          content_api.ProcessorContent(['foo', 'bar', 'baz']),
      )

  def test_chain_with_reserved_substreams(self):
    substreams_seen = set()

    @processor.part_processor_function
    async def mock_processor(
        content: processor.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      substreams_seen.add(content.substream_name)
      yield content

    chained = mock_processor + mock_processor
    content = [
        processor.ProcessorPart('data', substream_name='data'),
        processor.ProcessorPart('debug', substream_name='debug'),
    ]

    processor.apply_sync(chained, content)

    # Check that the debug substream was captured and not passed to the
    # processor
    self.assertEqual(substreams_seen, {'data'})

  def test_chained_processor_raises_specific_error_message(self):
    err_msg = 'bar is bad'

    @processor.processor_function
    async def processor_0(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for c in content:
        if c.text == 'bar':
          raise ValueError(err_msg)
        yield c

    # Using assertRaises removes the traceback which we want to check
    # includes the TaskGroup error.
    exception = None
    tb = None
    try:
      processor.apply_sync(
          processor_0, content_api.ProcessorContent(['foo', 'bar'])
      )
    except ValueError as e:
      exception = str(e)
      tb = traceback.format_exc()

    # Assert that the error message isn't a generic ExceptionGroup message
    self.assertNotIn('unhandled errors in a TaskGroup', exception)
    self.assertIn('unhandled errors in a TaskGroup', tb)
    self.assertEqual(exception, err_msg)

  def test_chained_part_processor_raises_specific_error_message(self):
    err_msg = 'bar is bad'

    @processor.part_processor_function
    async def processor_0(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      if part.text == 'bar':
        raise ValueError(err_msg)
      yield part

    combined_processor = processor.chain([processor_0])

    # Using assertRaises removes the traceback which we want to check
    # includes the TaskGroup error.
    exception = None
    tb = None
    try:
      processor.apply_sync(
          combined_processor, [content_api.ProcessorPart('bar')]
      )
    except ValueError as e:
      exception = str(e)
      tb = traceback.format_exc()

    # Assert that the error message isn't a generic ExceptionGroup message
    self.assertNotIn('unhandled errors in a TaskGroup', exception)
    self.assertIn('unhandled errors in a TaskGroup', tb)
    self.assertEqual(exception, err_msg)

  def test_normalization_function(self):
    @processor.processor_function
    async def yield_non_normalized_parts(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPartTypes]:
      """Demonstrates how part normalization works.

      Canonical representation for parts is ProcessorPart class. However often
      we need to deal with content not yet wrapped in-to ProcessorPart (raw
      strings, ganai.Part, PIL.Image) or parts wrapped in a container such as
      asyncio.Queue.

      Args:
        content: Incoming content. Note that it is always normalized.

      Yields:
        Various non normalized part representations.
      """
      # content_api.ProcessorPart can be yielded and no conversion would happen.
      # We don't support AsyncIterable normalization yet, so a loop is required
      # here.
      async for part in content:
        yield part

      # Strings become plain text chunks.
      yield 'Hello '
      # Gemini API parts can be yielded directly.
      yield genai_types.Part(text='world!')

    output = processor.apply_sync(
        yield_non_normalized_parts + _check_is_part,
        ['Agent: '],
    )
    self.assertEqual(content_api.as_text(output), 'Agent: Hello world!')

  def test_normalization_class(self):

    class YieldNonNormalizedParts(processor.Processor):
      """Demonstrates how part normalization works."""

      async def call(
          self,
          content: AsyncIterable[content_api.ProcessorPart],
      ) -> AsyncIterable[content_api.ProcessorPartTypes]:
        # content_api.ProcessorPart can be yielded and no conversion would
        # happen. We don't support AsyncIterable normalization yet, so a loop is
        # required here.
        async for part in content:
          yield part

        # Strings become plain text chunks.
        yield 'Hello '
        # Gemini API parts can be yielded directly.
        yield genai_types.Part(text='world!')

    output = processor.apply_sync(
        YieldNonNormalizedParts() + _check_is_part,
        ['Agent: '],
    )
    self.assertEqual(content_api.as_text(output), 'Agent: Hello world!')


class PartProcessorTest(unittest.TestCase):

  def test_part_processor_class(self):
    class Echo(processor.PartProcessor):

      def __init__(self):
        self.execute_order = []

      async def call(
          self, part: content_api.ProcessorPart
      ) -> AsyncIterable[content_api.ProcessorPart]:
        part_int = int(part.text)
        # Wait for duration inverse to content
        await asyncio.sleep(2 - part_int)

        self.execute_order.append(part_int)
        yield part

    echo_processor = Echo()

    debug_content = get_processor_parts(['0', '1', '2'])

    transformed_content = processor.apply_sync(echo_processor, debug_content)

    self.assertEqual(transformed_content, debug_content)
    self.assertEqual(echo_processor.execute_order, [2, 1, 0])

  def test_processor_fn_decorator(self):

    @processor.part_processor_function
    async def twice(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      yield part
      yield part

    inputs = [content_api.ProcessorPart('1')]
    content = processor.apply_sync(twice, inputs)
    self.assertEqual(content, inputs * 2)

    four_times = twice + twice
    content = processor.apply_sync(four_times, inputs)
    self.assertEqual(content, inputs * 4)

  def test_chain_class(self):

    class TwiceAgain(processor.PartProcessor):
      name: str = 'twice_again'

      def __init__(self):
        pass

      async def call(
          self, part: content_api.ProcessorPart
      ) -> AsyncIterable[content_api.ProcessorPart]:
        yield part
        yield part

      def print(self) -> str:
        return self.name

    inputs = [content_api.ProcessorPart('1')]
    part_processor = TwiceAgain()
    self.assertEqual(part_processor.name, 'twice_again')
    self.assertEqual(part_processor.print(), 'twice_again')
    content = processor.apply_sync(part_processor, inputs)
    self.assertEqual(content, inputs * 2)

    part_processor += part_processor
    content = processor.apply_sync(part_processor, inputs)
    self.assertEqual(content, inputs * 4)

  def test_chain_part_processor(self):
    @processor.part_processor_function
    async def twice(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      yield part
      yield part

    four_times = twice + twice
    inputs = [content_api.ProcessorPart('1')]
    content = processor.apply_sync(four_times, inputs)
    self.assertEqual(content, inputs * 4)

  def test_filter_part_processor(self):
    p = processor.create_filter(lambda part: part.text != '1')

    inputs = get_processor_parts(['1', '2', '1', '0'])
    content = processor.apply_sync(p, inputs)
    self.assertEqual(content, [inputs[1], inputs[3]])

    # Chaining filter is the same as an 'and' operation.
    q = processor.create_filter(lambda part: part.text != '2')
    content = processor.apply_sync(p + q, inputs)
    self.assertEqual(content, [inputs[3]])

    # Parallel op on filter is the same as an 'or' operation when the conditions
    # cover exclusive cases.
    inputs = get_processor_parts(['1', '2', '1'])
    content = processor.apply_sync(p // q, inputs)
    self.assertEqual(content, inputs)


class ProcessorTest(unittest.TestCase):

  def test_processor_fn_decorator(self):
    @processor.processor_function
    async def twotimes(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for c in content:
        yield c
        yield c

    inputs = [content_api.ProcessorPart('1')]
    content = processor.apply_sync(twotimes, inputs)
    self.assertEqual(content, inputs * 2)

    fourtimes = twotimes + twotimes
    content = processor.apply_sync(fourtimes, inputs)
    self.assertEqual(content, inputs * 4)

  def test_chain_class(self):
    class TwiceAgain(processor.Processor):
      name: str = 'twice_again'

      def __init__(self):
        pass

      async def call(
          self,
          content: AsyncIterable[content_api.ProcessorPart],
      ) -> AsyncIterable[content_api.ProcessorPart]:
        async for part in content:
          yield part
          yield part

      def print(self) -> str:
        return self.name

    inputs = [content_api.ProcessorPart('1')]
    content_processor = TwiceAgain()
    self.assertEqual(content_processor.name, 'twice_again')
    self.assertEqual(content_processor.print(), 'twice_again')
    content = processor.apply_sync(content_processor, inputs)
    self.assertEqual(content, inputs * 2)

    content_processor += content_processor
    content = processor.apply_sync(content_processor, inputs)
    self.assertEqual(content, inputs * 4)

  def test_chain_processor(self):
    @processor.processor_function
    async def twotimes(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for c in content:
        yield c
        yield c

    four_times = twotimes + twotimes
    inputs = [content_api.ProcessorPart('1')]
    content = processor.apply_sync(four_times, inputs)
    self.assertEqual(content, inputs * 4)

  def test_custom_reserved_substreams(self):
    substreams_seen = set()

    @processor.processor_function
    async def mock_processor(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for part in content:
        substreams_seen.add(part.substream_name)
        yield part

    # Chaining sends the reserved substreams straight to the output.
    chained = (mock_processor + mock_processor).to_processor()
    content = [
        processor.ProcessorPart('data', substream_name='data'),
        processor.ProcessorPart('debug', substream_name='custom_debug'),
    ]

    output_substream = set()

    async def run_with_context():
      async with processor.context(reserved_substreams=['custom_debug']):
        async for part in chained(streams.stream_content(content)):
          output_substream.add(part.substream_name)

    asyncio.run(run_with_context())

    # Check that the debug substream was captured and not passed to the
    # processor
    self.assertEqual(substreams_seen, {'data'})
    self.assertEqual(output_substream, {'data', 'custom_debug'})


class TestWithProcessors(unittest.TestCase):

  def setUp(self):
    super().setUp()

    @processor.processor_function
    async def twice(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for c in content:
        yield c
        yield c

    @processor.processor_function
    async def tozero(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for _ in content:
        yield content_api.ProcessorPart('0')

    @processor.part_processor_function
    async def insert_1(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      yield content_api.ProcessorPart('1')
      yield part

    @processor.part_processor_function
    async def insert_2(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      yield content_api.ProcessorPart('2')
      yield part

    # twice is a processor
    self.twice = twice
    self.tozero = tozero
    # insert
    self.insert_1 = insert_1
    self.insert_2 = insert_2


class ProcessorChainMixTest(TestWithProcessors):

  def setUp(self):
    super().setUp()
    # output when running insert_1 + insert_2 + insert_1 on '0'
    self.expected_1_2_1 = get_processor_parts(
        ['1', '2', '1', '1', '1', '2', '1', '0']
    )
    # output when running insert_1 + insert_2 + insert_1 + insert_2 on '0'
    self.expected_1_2_1_2 = []
    for part in self.expected_1_2_1:
      self.expected_1_2_1_2 += [content_api.ProcessorPart('2')] + [part]
    # output when running insert_1 + insert_1 + insert_2 on '0'
    self.expected_1_1_2 = get_processor_parts(
        ['2', '1', '2', '1', '2', '1', '2', '0']
    )
    # output when running twice + insert_1 + insert_2 on '0'
    self.expected_twice_1_2 = get_processor_parts(
        ['2', '1', '2', '0', '2', '1', '2', '0']
    )
    # output when running insert_1 + insert_2 + twice on '0'
    self.expected_1_2_twice = get_processor_parts(
        ['2', '2', '1', '1', '2', '2', '0', '0']
    )

  def test_processor_plus_processor(self):

    class TwiceAgain(processor.Processor):

      async def call(
          self,
          content: AsyncIterable[content_api.ProcessorPart],
      ) -> AsyncIterable[content_api.ProcessorPart]:
        async for part in content:
          yield part
          yield part

    inputs = [content_api.ProcessorPart('1')]
    twice_again = TwiceAgain()
    four_times = self.twice + twice_again
    content = processor.apply_sync(four_times, inputs)
    self.assertEqual(content, inputs * 4)
    four_times = twice_again + self.twice
    content = processor.apply_sync(four_times, inputs)
    self.assertEqual(content, inputs * 4)
    four_times = self.twice + self.twice
    content = processor.apply_sync(four_times, inputs)
    self.assertEqual(content, inputs * 4)
    four_times_zero = self.twice + self.twice + self.tozero
    content = processor.apply_sync(four_times_zero, inputs)
    self.assertEqual(content, [content_api.ProcessorPart('0')] * 4)

  def test_part_processor_pass_thru(self):
    p = processor.passthrough()
    inputs = [content_api.ProcessorPart('0')]

    q = p + self.insert_1 + p
    content = content_api.ProcessorContent(processor.apply_sync(q, inputs))
    self.assertEqual(content_api.as_text(content), '10')
    # self.assertIsInstance(self, q, processor._ChainPartProcessor)
    self.assertEqual(
        cast(processor._ChainPartProcessor, q)._processor_list,
        [self.insert_1],
    )

    r = p + p + self.insert_1
    content = processor.apply_sync(r, inputs)
    self.assertEqual(content_api.as_text(content), '10')

    s = self.insert_1 + p + self.insert_1
    content = processor.apply_sync(s, inputs)
    self.assertEqual(content_api.as_text(content), '1110')

    u = self.insert_1 + p + p
    content = processor.apply_sync(u, inputs)
    self.assertEqual(content_api.as_text(content), '10')

    v = self.insert_1 + self.insert_1
    w = p + v
    # This assignment should not change w (twice called x2).
    v = v + self.insert_1  # pylint: disable=unused-variable
    content = processor.apply_sync(w, inputs)
    self.assertEqual(content_api.as_text(content), '1110')

  def test_processor_plus_partprocessor(self):
    inputs = [content_api.ProcessorPart('0')]
    expected = get_processor_parts(['1', '0', '1', '0'])
    chain = self.twice + self.insert_1
    self.assertEqual(processor.apply_sync(chain, inputs), expected)
    expected = get_processor_parts(['1', '1', '0', '0'])
    chain = self.insert_1 + self.twice
    self.assertEqual(processor.apply_sync(chain, inputs), expected)

  def test_processor_plus_chainpartprocessor(self):
    # Test combinations of processors with chainpartprocessors using '+'.
    # We will combine twice + insert_1 + insert_2 in different ways below.
    # twice is a Processor, insert_1 and insert_2 are PartProcessors
    inputs = [content_api.ProcessorPart('0')]
    chain = self.twice + (self.insert_1 + self.insert_2)
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_twice_1_2
    )
    # Same as above but without caching
    chain = self.twice + (self.insert_1 + self.insert_2)
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_twice_1_2
    )
    chain = self.twice
    chain += self.insert_1 + self.insert_2
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_twice_1_2
    )

    # Start with part processor chain and add a processor at the end.
    chain = (self.insert_1 + self.insert_2) + self.twice
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_1_2_twice
    )
    chain = (self.insert_1 + self.insert_2) + self.twice
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_1_2_twice
    )

  def test_processor_plus_chainprocessor(self):
    inputs = [content_api.ProcessorPart('0')]
    chain = self.twice + (
        self.insert_1.to_processor() + self.insert_2.to_processor()
    )
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_twice_1_2
    )
    chain = self.twice
    chain += self.insert_1.to_processor() + self.insert_2.to_processor()
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_twice_1_2
    )
    chain = (
        self.twice + self.insert_1.to_processor() + self.insert_2.to_processor()
    )
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_twice_1_2
    )
    chain = (
        self.insert_1.to_processor() + self.insert_2.to_processor()
    ) + self.twice
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_1_2_twice
    )
    chain = self.insert_1.to_processor() + self.insert_2.to_processor()
    chain += self.twice
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_1_2_twice
    )
    chain = (
        self.insert_1.to_processor() + self.insert_2.to_processor() + self.twice
    )
    self.assertEqual(
        processor.apply_sync(chain, inputs), self.expected_1_2_twice
    )

  def test_partprocessor_plus_chainpartprocessor(self):
    inputs = [content_api.ProcessorPart('0')]
    # Test part processor + chain part processor
    chain = self.insert_1 + (self.insert_1 + self.insert_2)
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_1_2)
    # Same as above but without caching
    chain = self.insert_1 + (self.insert_1 + self.insert_2)
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_1_2)
    chain = self.insert_1
    chain += self.insert_1 + self.insert_2
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_1_2)
    chain = self.insert_1 + self.insert_1 + self.insert_2
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_1_2)

    # Tets chain part processor + part processor
    chain = (self.insert_1 + self.insert_2) + self.insert_1
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_2_1)
    chain = (self.insert_1 + self.insert_2) + self.insert_1
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_2_1)

  def test_partprocessor_plus_chainprocessor(self):
    inputs = [content_api.ProcessorPart('0')]
    chain = self.insert_1 + (
        self.insert_1.to_processor() + self.insert_2.to_processor()
    )
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_1_2)
    chain = self.insert_1
    chain += self.insert_1.to_processor() + self.insert_2.to_processor()
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_1_2)
    chain = (
        self.insert_1
        + self.insert_1.to_processor()
        + self.insert_2.to_processor()
    )
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_1_2)
    chain = (
        self.insert_1.to_processor() + self.insert_2.to_processor()
    ) + self.insert_1
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_2_1)
    chain = self.insert_1.to_processor() + self.insert_2.to_processor()
    chain += self.insert_1
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_2_1)
    chain = (
        self.insert_1.to_processor()
        + self.insert_2.to_processor()
        + self.insert_1
    )
    self.assertEqual(processor.apply_sync(chain, inputs), self.expected_1_2_1)

  def test_chainprocessor_plus_chainprocessor(self):
    inputs = [content_api.ProcessorPart('0')]
    chain = (self.twice + self.insert_2.to_processor()) + (
        self.insert_1.to_processor() + self.tozero
    )
    self.assertIsInstance(chain, processor._ChainProcessor)
    self.assertEqual(
        processor.apply_sync(chain, inputs),
        [content_api.ProcessorPart('0')] * 8,
    )

  def test_chainpartprocessor_plus_chainpartprocessor(self):
    inputs = [content_api.ProcessorPart('0')]
    chain = (self.insert_1 + self.insert_2) + (self.insert_1 + self.insert_2)
    self.assertIsInstance(chain, processor._ChainPartProcessor)
    self.assertEqual(
        processor.apply_sync(chain, inputs),
        self.expected_1_2_1_2,
    )

  def test_chainprocessor_plus_chainpartprocessor(self):
    inputs = [content_api.ProcessorPart('0')]
    chain = (self.insert_1.to_processor() + self.insert_2.to_processor()) + (
        self.insert_1 + self.insert_2
    )
    self.assertIsInstance(chain, processor._ChainProcessor)
    self.assertEqual(
        processor.apply_sync(chain, inputs),
        self.expected_1_2_1_2,
    )

  def test_chain_processors(self):
    inputs = [content_api.ProcessorPart('0')]
    chain = processor.chain([self.twice, self.twice])
    content = processor.apply_sync(chain, inputs)
    self.assertEqual(content, inputs * 4)
    chain = processor.chain([self.insert_1, self.insert_2, self.insert_1])
    content = processor.apply_sync(chain, inputs)
    self.assertEqual(content, self.expected_1_2_1)
    chain = processor.chain([
        self.insert_1.to_processor(),
        self.insert_2,
        self.insert_1.to_processor(),
    ])
    content = processor.apply_sync(chain, inputs)
    self.assertEqual(content, self.expected_1_2_1)
    chain = processor.chain(
        [self.insert_1, self.insert_2.to_processor(), self.insert_1]
    )
    content = processor.apply_sync(chain, inputs)
    self.assertEqual(content, self.expected_1_2_1)
    chain = processor.chain([
        self.insert_1.to_processor(),
        self.insert_2.to_processor(),
        self.insert_1.to_processor(),
    ])
    content = processor.apply_sync(chain, inputs)
    self.assertEqual(content, self.expected_1_2_1)
    chain = processor.chain([self.insert_1, self.insert_2]) + self.insert_1
    content = processor.apply_sync(chain, inputs)
    self.assertEqual(content, self.expected_1_2_1)
    chain = processor.chain([(self.insert_1 + self.insert_2), self.twice])
    content = processor.apply_sync(chain, inputs)
    self.assertEqual(content, self.expected_1_2_twice)
    chain = processor.chain([(self.insert_1 + self.insert_2), self.twice])
    content = processor.apply_sync(chain, inputs)
    self.assertEqual(content, self.expected_1_2_twice)
    chain = processor.chain([self.twice, self.twice])
    content = processor.apply_sync(chain, inputs)
    self.assertEqual(content, inputs * 4)

  def test_chain_immutable(self):

    @processor.processor_function
    async def ones(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for _ in content:
        yield content_api.ProcessorPart('1')

    @processor.processor_function
    async def twos(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for _ in content:
        yield content_api.ProcessorPart('2')

    @processor.processor_function
    async def threes(
        content: AsyncIterable[content_api.ProcessorPart],
    ) -> AsyncIterable[content_api.ProcessorPart]:
      async for _ in content:
        yield content_api.ProcessorPart('3')

    should_yield_twos = processor.chain([ones, twos])

    should_yield_threes = processor.chain([should_yield_twos, threes])

    inputs = get_processor_parts(['0'])

    self.assertEqual(
        processor.apply_sync(ones, inputs), get_processor_parts(['1'])
    )
    self.assertEqual(
        processor.apply_sync(should_yield_twos, inputs),
        get_processor_parts(['2']),
    )
    self.assertEqual(
        processor.apply_sync(should_yield_threes, inputs),
        get_processor_parts(['3']),
    )

  def test_custom_reserved_substreams(self):
    substreams_seen = set()

    @processor.part_processor_function
    async def mock_processor(
        content: processor.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      substreams_seen.add(content.substream_name)
      yield content

    # Chaining sends the reserved substreams straight to the output.
    chained = (mock_processor + mock_processor).to_processor()
    content = [
        processor.ProcessorPart('data', substream_name='data'),
        processor.ProcessorPart('debug', substream_name='custom_debug'),
    ]

    output_substream = set()

    async def run_with_context():
      async with processor.context(reserved_substreams=['custom_debug']):
        async for part in chained(streams.stream_content(content)):
          output_substream.add(part.substream_name)

    asyncio.run(run_with_context())

    # Check that the debug substream was captured and not passed to the
    # processor
    self.assertEqual(substreams_seen, {'data'})
    self.assertEqual(output_substream, {'data', 'custom_debug'})

  def test_chain_processor_with_match_fn(self):
    task_count = 0

    @processor.part_processor_function(
        match_fn=lambda x: x.text.startswith('0')
    )
    async def add_one(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      nonlocal task_count
      task_count += 1
      if part.text.startswith('0'):
        yield content_api.ProcessorPart(part.text + '1')
      else:
        yield part

    chain = add_one + add_one
    content = processor.apply_sync(chain, get_processor_parts(['0', '1']))
    self.assertEqual(content, get_processor_parts(['011', '1']))
    content = processor.apply_sync(chain, get_processor_parts(['1', '2']))
    self.assertEqual(content, get_processor_parts(['1', '2']))
    self.assertEqual(task_count, 2)

    task_count = 0
    long_chain = processor.chain([add_one] * 100)
    content = processor.apply_sync(long_chain, get_processor_parts(['1']))
    self.assertEqual(content, get_processor_parts(['1']))
    self.assertEqual(task_count, 0)

    task_count = 0
    chain = self.insert_1 + add_one + self.insert_2 + add_one
    content = processor.apply_sync(chain, get_processor_parts(['0']))
    self.assertEqual(content, get_processor_parts(['2', '1', '2', '011']))
    self.assertEqual(task_count, 2)


class ParallelProcessorsTest(TestWithProcessors):

  def test_parallel_processors(self):
    inputs = [content_api.ProcessorPart('1')]
    parallel_c = processor.parallel_concat([self.twice, self.tozero])
    content = processor.apply_sync(parallel_c, inputs)
    self.assertEqual(content, get_processor_parts(['1', '1', '0']))
    parallel_c = processor.chain([
        parallel_c,
        self.twice,
    ])
    content = processor.apply_sync(parallel_c, inputs)
    self.assertEqual(
        content, get_processor_parts(['1', '1', '1', '1', '0', '0'])
    )
    inputs = [content_api.ProcessorPart('1'), content_api.ProcessorPart('2')]
    parallel_c = processor.parallel_concat([self.twice, self.tozero])
    content = processor.apply_sync(parallel_c, inputs)
    self.assertEqual(
        content,
        get_processor_parts(['1', '1', '2', '2', '0', '0']),
    )

  def test_parallel_part_processors(self):
    inputs = [content_api.ProcessorPart('0')]
    parallel_p = processor.parallel([self.insert_1, self.insert_2])
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(content, get_processor_parts(['1', '0', '2', '0']))
    parallel_p = processor.chain([
        parallel_p,
        self.insert_1,
    ])
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content, get_processor_parts(['1', '1', '1', '0', '1', '2', '1', '0'])
    )
    inputs = [content_api.ProcessorPart('0'), content_api.ProcessorPart('1')]
    parallel_p = processor.parallel([self.insert_1, self.insert_2])
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content,
        get_processor_parts(['1', '0', '2', '0', '1', '1', '2', '1']),
    )
    parallel_content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(content, parallel_content)
    inputs = [content_api.ProcessorPart('0')]
    parallel_p = processor.parallel(
        [(self.insert_1 + self.insert_2), self.insert_1]
    )
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content, get_processor_parts(['2', '1', '2', '0', '1', '0'])
    )

  def test_parallel_operator(self):
    inputs = [content_api.ProcessorPart('0')]
    parallel_p = self.insert_1 // self.insert_2
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(content, get_processor_parts(['1', '0', '2', '0']))
    parallel_p = parallel_p // self.insert_1
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content, get_processor_parts(['1', '0', '2', '0', '1', '0'])
    )
    inputs = [content_api.ProcessorPart('0'), content_api.ProcessorPart('1')]
    parallel_p = self.insert_1 // self.insert_2
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content,
        get_processor_parts(['1', '0', '2', '0', '1', '1', '2', '1']),
    )
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content,
        get_processor_parts(['1', '0', '2', '0', '1', '1', '2', '1']),
    )
    parallel_content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(content, parallel_content)
    inputs = [content_api.ProcessorPart('0')]
    parallel_p = (self.insert_1 + self.insert_2) // self.insert_1
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content, get_processor_parts(['2', '1', '2', '0', '1', '0'])
    )
    # // has higher precedence over +. This is equivalent to:
    # (insert_1 // insert_2) + (insert_1 // insert_2)
    parallel_p = self.insert_1 // self.insert_2 + self.insert_1 // self.insert_2
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content,
        get_processor_parts([
            '1',
            '1',
            '2',
            '1',
            '1',
            '0',
            '2',
            '0',
            '1',
            '2',
            '2',
            '2',
            '1',
            '0',
            '2',
            '0',
        ]),
    )

  def test_parallel_operator_with_fallback(self):

    @processor.part_processor_function
    async def add_one_maybe(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      if part.text.startswith('0'):
        yield content_api.ProcessorPart(part.text + '1')

    @processor.part_processor_function
    async def add_one(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      yield content_api.ProcessorPart(part.text + '1')

    inputs = get_processor_parts(['0', '1'])
    # Check std fallback gives output when nothing is returned by other
    # processors.
    parallel_p = add_one + (
        add_one_maybe // add_one_maybe // processor.PASSTHROUGH_FALLBACK
    )
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(content, get_processor_parts(['011', '011', '11']))

    # Check fall_back plays well with passthrough_always.
    parallel_p = add_one + (
        add_one_maybe
        // (add_one_maybe // processor.PASSTHROUGH_ALWAYS)
        // processor.PASSTHROUGH_FALLBACK
    )
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(content, get_processor_parts(['011', '011', '01', '11']))

    parallel_p = (add_one_maybe // processor.PASSTHROUGH_ALWAYS) + (
        add_one_maybe // processor.PASSTHROUGH_FALLBACK
    )
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(content, get_processor_parts(['011', '01', '1']))

    # Check no fallback can lead to no output.
    parallel_p = add_one_maybe // add_one_maybe
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content,
        get_processor_parts(['01', '01']),
    )

  def test_parallel_operator_with_passthrough_always(self):

    @processor.part_processor_function
    async def add_one(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      if part.text.startswith('0'):
        yield content_api.ProcessorPart(part.text + '1')

    inputs = get_processor_parts(['0', '1'])
    parallel_p = add_one // add_one // processor.PASSTHROUGH_ALWAYS
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(content, get_processor_parts(['01', '01', '0', '1']))
    parallel_p = (
        add_one
        // add_one
        // processor.PASSTHROUGH_ALWAYS
        // processor.PASSTHROUGH_FALLBACK
    )
    content = processor.apply_sync(parallel_p, inputs)
    self.assertEqual(
        content,
        get_processor_parts(['01', '01', '0', '1']),
    )

  def test_reserved_substreams_returned_first(self):

    @processor.part_processor_function
    async def add_two_with_status(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      yield processor.status('2 status')
      await asyncio.sleep(1)
      yield content_api.ProcessorPart(part.text + '2')

    @processor.part_processor_function
    async def add_three_with_debug(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      yield processor.debug('3 debug')
      await asyncio.sleep(1)
      yield content_api.ProcessorPart(part.text + '3')

    @processor.part_processor_function
    async def identity(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      yield part

    p = (
        identity
        + self.insert_1
        + (
            add_two_with_status
            // add_three_with_debug
            // processor.PASSTHROUGH_ALWAYS
        )
    )
    result = processor.apply_sync(p, [content_api.ProcessorPart('0')])
    self.assertEqual(len(result), 10)
    # The first results should be the status or debug streams before the sleep.
    for i in range(3):
      self.assertIn(result[i].substream_name, ['status', 'debug'])

  def test_custom_reserved_substreams(self):
    substreams_seen = set()

    @processor.part_processor_function
    async def mock_processor(
        content: processor.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      substreams_seen.add(content.substream_name)
      yield content

    # Chaining sends the reserved substreams straight to the output.
    chained = (mock_processor // mock_processor).to_processor()
    content = [
        processor.ProcessorPart('data', substream_name='data'),
        processor.ProcessorPart('debug', substream_name='custom_debug'),
    ]

    output_substream = set()

    async def run_with_context():
      async with processor.context(reserved_substreams=['custom_debug']):
        async for part in chained(streams.stream_content(content)):
          output_substream.add(part.substream_name)

    asyncio.run(run_with_context())

    # Check that the debug substream was captured and not passed to the
    # processor
    self.assertEqual(substreams_seen, {'data'})
    self.assertEqual(output_substream, {'data', 'custom_debug'})

  def test_process_with_valid_fn_ok(self):
    task_count = 0

    @processor.part_processor_function(
        match_fn=lambda part: part.text.startswith('0')
    )
    async def add_one(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      nonlocal task_count
      task_count += 1
      if part.text.startswith('0'):
        yield content_api.ProcessorPart(part.text + '1')
      else:
        yield part

    parallel = add_one // add_one // processor.PASSTHROUGH_FALLBACK
    parallel = cast(processor._ParallelPartProcessor, parallel)
    self.assertTrue(parallel.match(content_api.ProcessorPart('0')))
    self.assertFalse(parallel.match(content_api.ProcessorPart('1')))
    content = processor.apply_sync(parallel, get_processor_parts(['2', '1']))
    self.assertEqual(content, get_processor_parts(['2', '1']))
    self.assertEqual(task_count, 0)

    task_count = 0
    content = processor.apply_sync(parallel, get_processor_parts(['0', '1']))
    self.assertEqual(content, get_processor_parts(['01', '01', '1']))
    self.assertEqual(task_count, 2)

    task_count = 0
    parallel = add_one // add_one
    parallel = cast(processor._ParallelPartProcessor, parallel)
    self.assertTrue(parallel.match(content_api.ProcessorPart('0')))
    self.assertTrue(parallel.match(content_api.ProcessorPart('1')))
    content = processor.apply_sync(parallel, get_processor_parts(['1', '1']))
    # The parallel processor is called and processes the parts but the
    # add_one processors are not called because the parts should not be
    # processed by them. The // operator implementation ensures that no part is
    # returned then. That's why match is true for the parallel
    # processor but not for the add_one processors.
    self.assertEqual(len(content), 0)
    self.assertEqual(task_count, 0)


class ErrorPropagationTest(
    parameterized.TestCase, unittest.IsolatedAsyncioTestCase
):

  @parameterized.parameters([True, False])
  async def test_error_propagation(self, parallel):

    @processor.part_processor_function
    async def processor_0(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      if part.text == 'foo':
        raise ValueError('foo is not allowed')
      yield part

    @processor.part_processor_function
    async def processor_1(
        part: content_api.ProcessorPart,
    ) -> AsyncIterable[content_api.ProcessorPart]:
      yield part

    # Check that the error is propagated before the test part is read.
    if parallel:
      p = processor.parallel([processor_0, processor_1]).to_processor()
    else:
      p = processor.chain([processor_0, processor_1])
    with self.assertRaises(ValueError):
      async for c in p(
          streams.stream_content(
              content_api.ProcessorContent(['foo', 'bar', 'test']).all_parts,
              with_delay_sec=0.01,
              delay_first=True,
          )
      ):
        if c.text == 'test':
          self.fail(
              'The exception should be propagated before the test part is read.'
          )
    # Same test with processors instead of part processors
    if parallel:
      q = processor.parallel_concat(
          [processor_0.to_processor(), processor_1.to_processor()]
      )
    else:
      q = processor.chain(
          [processor_0.to_processor(), processor_1.to_processor()]
      )
    with self.assertRaises(ValueError):
      async for c in q(
          streams.stream_content(
              content_api.ProcessorContent(['foo', 'bar', 'test']).all_parts,
              with_delay_sec=0.01,
              delay_first=True,
          )
      ):
        # We should fail before reaching 'test'.
        if c.text == 'test':
          self.fail(
              'The exception should be propagated before the test part is read.'
          )


class YieldExceptionsAsPartsTest(
    parameterized.TestCase, unittest.IsolatedAsyncioTestCase
):

  async def test_decorator_creates_structured_error_part(self):

    class FailingProcessor(processor.PartProcessor):

      @processor.yield_exceptions_as_parts
      async def call(
          self, part: content_api.ProcessorPart
      ) -> AsyncIterable[content_api.ProcessorPart]:
        if part.text == 'b':
          raise ValueError("I don't like b.")
        yield part

    failing_processor = FailingProcessor()
    parts = get_processor_parts(['a', 'b', 'c'])
    results = await processor.apply_async(failing_processor, parts)

    # We expect three parts back: 'a', 'c', and one error part for 'b'.
    self.assertEqual(len(results), 3)  # pylint: disable=g-generic-assert

    error_parts = [p for p in results if mime_types.is_exception(p.mimetype)]
    successful_parts = [
        p for p in results if not mime_types.is_exception(p.mimetype)
    ]

    self.assertEqual(len(successful_parts), 2)
    self.assertEqual({p.text for p in successful_parts}, {'a', 'c'})  # pylint: disable=g-generic-assert

    self.assertEqual(len(error_parts), 1)  # pylint: disable=g-generic-assert
    error_part = error_parts[0]

    self.assertEqual(error_part.substream_name, processor.STATUS_STREAM)
    self.assertEqual(error_part.mimetype, mime_types.TEXT_EXCEPTION)

    self.assertIn("I don't like b.", error_part.text)

    self.assertIsNotNone(error_part.metadata)
    self.assertIn(
        "I don't like b.", error_part.metadata.get('original_exception')
    )
    self.assertEqual('ValueError', error_part.metadata.get('exception_type'))

  async def test_decorator_does_not_interfere_when_no_exception(self):

    class DoublingProcessor(processor.PartProcessor):

      @processor.yield_exceptions_as_parts
      async def call(
          self, part: content_api.ProcessorPart
      ) -> AsyncIterable[content_api.ProcessorPart]:
        yield part
        yield part

    doubling_processor = DoublingProcessor()
    parts = get_processor_parts(['a', 'b'])
    results = await processor.apply_async(doubling_processor, parts)

    self.assertEqual(len(results), 4)  # pylint: disable=g-generic-assert
    result_texts = sorted([p.text for p in results])
    self.assertEqual(result_texts, ['a', 'a', 'b', 'b'])


if __name__ == '__main__':
  unittest.main()
