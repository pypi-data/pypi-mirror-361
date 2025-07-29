import asyncio
import unittest
from unittest import mock

from genai_processors import cache
from genai_processors import content_api


ProcessorPart = content_api.ProcessorPart
ProcessorContent = content_api.ProcessorContent


class InMemoryCacheTest(unittest.IsolatedAsyncioTestCase):

  async def test_put_and_lookup_with_default_hash(self):
    """Tests basic put and lookup using the default hashing."""
    mem_cache = cache.InMemoryCache(max_items=10, ttl_hours=1)
    query = ProcessorContent(['query_text'])
    value_content = ProcessorContent(
        [ProcessorPart('response_text', role='model')]
    )
    await mem_cache.put(query, value_content)
    retrieved = await mem_cache.lookup(query)

    self.assertIsNot(retrieved, cache.CacheMiss)
    self.assertEqual(content_api.as_text(retrieved), 'response_text')

  async def test_lookup_miss(self):
    """Tests that a lookup for a non-existent key returns CacheMiss."""
    mem_cache = cache.InMemoryCache()
    retrieved = await mem_cache.lookup(ProcessorContent(['non_existent_key']))
    self.assertIs(retrieved, cache.CacheMiss)

  async def test_put_override(self):
    mem_cache = cache.InMemoryCache()
    query = ProcessorContent(['query_text'])
    await mem_cache.put(query, ProcessorContent(['value1']))
    await mem_cache.put(query, ProcessorContent(['value2']))

    retrieved = await mem_cache.lookup(query)
    self.assertIsNot(retrieved, cache.CacheMiss)
    self.assertEqual(content_api.as_text(retrieved), 'value2')

  async def test_ttl_expiration(self):
    """Tests that an item expires after its TTL."""
    ttl_hours = 0.0001  # A very short TTL
    mem_cache = cache.InMemoryCache(ttl_hours=ttl_hours, max_items=10)
    query = ProcessorContent(['key1'])
    await mem_cache.put(query, ProcessorContent(['value1']))

    # Should exist immediately after
    self.assertIsNot(await mem_cache.lookup(query), cache.CacheMiss)

    # Wait for more than the TTL
    await asyncio.sleep(ttl_hours * 3600 * 1.1)
    self.assertIs(await mem_cache.lookup(query), cache.CacheMiss)

  async def test_max_items_eviction(self):
    mem_cache = cache.InMemoryCache(max_items=2)
    query1 = ProcessorContent(['key1'])
    query2 = ProcessorContent(['key2'])
    query3 = ProcessorContent(['key3'])

    await mem_cache.put(query1, ProcessorContent(['value1']))
    await mem_cache.put(query2, ProcessorContent(['value2']))
    await mem_cache.put(
        query3, ProcessorContent(['value3'])
    )  # This should evict query1

    # query1 should be gone
    self.assertIs(await mem_cache.lookup(query1), cache.CacheMiss)
    # query2 and query3 should still be present
    self.assertIsNot(await mem_cache.lookup(query2), cache.CacheMiss)
    self.assertIsNot(await mem_cache.lookup(query3), cache.CacheMiss)

  async def test_remove(self):
    mem_cache = cache.InMemoryCache()
    query = ProcessorContent(['key1'])
    await mem_cache.put(query, ProcessorContent(['value1']))
    self.assertIsNot(await mem_cache.lookup(query), cache.CacheMiss)

    await mem_cache.remove(query)
    self.assertIs(await mem_cache.lookup(query), cache.CacheMiss)

  async def test_uses_custom_hash_function(self):
    custom_hash_fn = mock.Mock(return_value='custom_key_123')
    mem_cache = cache.InMemoryCache(hash_fn=custom_hash_fn)
    query = ProcessorContent(['query_text'])

    await mem_cache.put(query, ProcessorContent(['value']))
    custom_hash_fn.assert_called_once_with(query)

    custom_hash_fn.reset_mock()
    await mem_cache.lookup(query)
    custom_hash_fn.assert_called_once_with(query)

  async def test_with_key_prefix_isolates_caches(self):
    cache1 = cache.InMemoryCache(max_items=10)
    cache2 = cache1.with_key_prefix('p_')

    self.assertIsNot(cache1, cache2)
    self.assertIsNot(
        cache1._cache, cache2._cache
    )  # Important: they have different TTLCache instances
    self.assertIsInstance(cache2, cache.InMemoryCache)
    self.assertEqual(cache1._max_items, cache2._max_items)

    query = ProcessorContent(['shared_query'])
    await cache1.put(query, ProcessorContent(['value1']))
    await cache2.put(query, ProcessorContent(['value2']))

    # Check that each cache has its own value for the same query
    retrieved1 = await cache1.lookup(query)
    retrieved2 = await cache2.lookup(query)

    self.assertIsNot(retrieved1, cache.CacheMiss)
    self.assertIsNot(retrieved2, cache.CacheMiss)
    self.assertEqual(content_api.as_text(retrieved1), 'value1')
    self.assertEqual(content_api.as_text(retrieved2), 'value2')

  async def test_hash_fn_returns_none(self):
    mem_cache = cache.InMemoryCache(hash_fn=lambda q: None)
    query = ProcessorContent(['any_query'])

    await mem_cache.put(query, ProcessorContent(['some_response']))
    self.assertIs(await mem_cache.lookup(query), cache.CacheMiss)

  async def test_hash_fn_raises_exception(self):
    mock_hash_fn = mock.Mock(side_effect=ValueError('Hashing failed!'))
    mem_cache = cache.InMemoryCache(hash_fn=mock_hash_fn)
    query = ProcessorContent(['query_that_will_fail_hash'])

    await mem_cache.put(query, ProcessorContent(['irrelevant']))
    self.assertIs(await mem_cache.lookup(query), cache.CacheMiss)
    self.assertEqual(mock_hash_fn.call_count, 2)

  async def test_put_with_serialization_error_propagates(self):
    mem_cache = cache.InMemoryCache()
    query = ProcessorContent(['query'])

    with mock.patch.object(
        mem_cache, '_serialize_fn', side_effect=RuntimeError('Unexpected!')
    ):
      with self.assertRaises(RuntimeError):
        await mem_cache.put(query, ProcessorContent(['irrelevant']))

  async def test_invalid_init_with_zero_max_items(self):
    with self.assertRaisesRegex(
        ValueError, 'max_items must be positive, got: 0'
    ):
      cache.InMemoryCache(max_items=0)

    with self.assertRaisesRegex(
        ValueError, 'max_items must be positive, got: -1'
    ):
      cache.InMemoryCache(max_items=-1)

  async def test_default_hash_is_part_order_sensitive(self):
    """Tests the default hash function's sensitivity to part order."""
    mem_cache = cache.InMemoryCache(max_items=10)
    part1 = ProcessorPart('Hello', role='user')
    part2 = ProcessorPart('World', role='user')
    value = ProcessorContent(['Response'])

    query_order1 = ProcessorContent([part1, part2])
    query_order2 = ProcessorContent([part2, part1])

    # Hashes should be different
    hash1 = cache.default_processor_content_hash(query_order1)
    hash2 = cache.default_processor_content_hash(query_order2)
    self.assertNotEqual(hash1, hash2)

    # Caching one should not allow lookup of the other
    await mem_cache.put(query_order1, value)
    self.assertIsNot(await mem_cache.lookup(query_order1), cache.CacheMiss)
    self.assertIs(await mem_cache.lookup(query_order2), cache.CacheMiss)

  async def test_default_hash_is_key_order_insensitive(self):
    """Tests the hash is insensitive to a part's internal dict key order."""
    mem_cache = cache.InMemoryCache(max_items=10)
    part_dict_1 = {'role': 'model', 'part': {'text': 'response text'}}
    part_dict_2 = {'part': {'text': 'response text'}, 'role': 'model'}

    query1 = ProcessorContent([ProcessorPart.from_dict(data=part_dict_1)])
    query2 = ProcessorContent([ProcessorPart.from_dict(data=part_dict_2)])
    value = ProcessorContent(['Value'])

    # Hashes should be identical because json.dumps uses sort_keys=True.
    hash1 = cache.default_processor_content_hash(query1)
    hash2 = cache.default_processor_content_hash(query2)
    self.assertEqual(hash1, hash2)

    await mem_cache.put(query1, value)
    retrieved = await mem_cache.lookup(query2)
    self.assertIsNot(retrieved, cache.CacheMiss)
    self.assertEqual(content_api.as_text(retrieved), 'Value')


if __name__ == '__main__':
  unittest.main()
