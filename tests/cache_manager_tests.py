import asynctest
import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call


class CacheManagerTestCase(asynctest.TestCase):
    """Test case for CacheManager class."""

    async def setUp(self):
        """Set up the test case environment."""
        from app.managers.cache_manager import CacheManager

        self.cache_mock = AsyncMock()
        self.cache_manager = CacheManager(self.cache_mock)

    async def tearDown(self):
        """Clean up the test case environment."""
        del self.cache_mock
        del self.cache_manager

    async def test__init(self):
        """Test CacheManager initialization."""
        self.assertEqual(self.cache_manager.cache, self.cache_mock)

    async def test__get_key_int(self):
        """Test _get_key method with integer id."""
        dummy_mock = MagicMock(__tablename__="dummies")

        result = self.cache_manager._get_key(dummy_mock, 123)
        self.assertEqual(result, "dummies:123")

    async def test__get_key_asterisk(self):
        """Test _get_key method with asterisk id."""
        dummy_mock = MagicMock(__tablename__="dummies")

        result = self.cache_manager._get_key(dummy_mock, "*")
        self.assertEqual(result, "dummies:*")

    @patch("app.managers.cache_manager.cfg")
    @patch("app.managers.cache_manager.dumps")
    async def test__cache_manager_set(self, dumps_mock, cfg_mock):
        """Test set method of CacheManager."""
        dummy_mock = MagicMock(__tablename__="dummies", id=123)

        result = await self.cache_manager.set(dummy_mock)
        self.assertIsNone(result)

        dumps_mock.assert_called_once()
        dumps_mock.assert_called_with(dummy_mock)

        self.cache_mock.set.assert_called_once()
        self.cache_mock.set.assert_called_with(
            "dummies:123", dumps_mock.return_value, ex=cfg_mock.REDIS_EXPIRE)

    @patch("app.managers.cache_manager.loads")
    async def test__cache_manager_get(self, loads_mock):
        """Test get method of CacheManager."""
        dummy_class_mock = MagicMock(__tablename__="dummies")

        result = await self.cache_manager.get(dummy_class_mock, 123)
        self.assertEqual(result, loads_mock.return_value)

        self.cache_mock.get.assert_called_once()
        self.cache_mock.get.assert_called_with("dummies:123")

        loads_mock.assert_called_once()
        loads_mock.assert_called_with(self.cache_mock.get.return_value)

    @patch("app.managers.cache_manager.loads")
    async def test__cache_manager_get_none(self, loads_mock):
        """Test get method of CacheManager when no data is found."""
        self.cache_mock.get.return_value = None
        dummy_class_mock = MagicMock(__tablename__="dummies")

        result = await self.cache_manager.get(dummy_class_mock, 123)
        self.assertIsNone(result)

        self.cache_mock.get.assert_called_once()
        self.cache_mock.get.assert_called_with("dummies:123")

        loads_mock.assert_not_called()

    async def test__cache_manager_delete(self):
        """Test delete method of CacheManager."""
        dummy_mock = MagicMock(__tablename__="dummies", id=123)

        result = await self.cache_manager.delete(dummy_mock)
        self.assertIsNone(result)

        self.cache_mock.delete.assert_called_once()
        self.cache_mock.delete.assert_called_with("dummies:123")

    async def test__cache_manager_delete_all(self):
        """Test delete_all method of CacheManager."""
        dummy_class_mock = MagicMock(__tablename__="dummies")
        key_1, key_2, key_3 = "dummies:1", "dummies:2", "dummies:3"
        self.cache_mock.keys.return_value = [key_1, key_2, key_3]

        result = await self.cache_manager.delete_all(dummy_class_mock)
        self.assertIsNone(result)

        self.cache_mock.keys.assert_called_once()
        self.cache_mock.keys.assert_called_with("dummies:*")

        self.assertEqual(self.cache_mock.delete.call_count, 3)
        self.assertListEqual(self.cache_mock.delete.call_args_list,
                             [call(key_1), call(key_2), call(key_3)])


if __name__ == "__main__":
    unittest.main()
