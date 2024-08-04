import asynctest
import unittest
from unittest.mock import MagicMock, AsyncMock
from app.repositories.album_repository import AlbumRepository
from app.models.album_models import Album


class AlbumRepositoryTestCase(asynctest.TestCase):

    def setUp(self):
        self.entity_manager_mock = AsyncMock()
        self.cache_manager_mock = AsyncMock()

        album_repository = AlbumRepository(None, None, Album)
        album_repository.entity_manager = self.entity_manager_mock
        album_repository.cache_manager = self.cache_manager_mock

        self.album_repository = album_repository

    def tearDown(self):
        del self.entity_manager_mock
        del self.cache_manager_mock
        del self.album_repository

    def test__album_repository_init(self):
        from app.managers.entity_manager import EntityManager
        from app.managers.cache_manager import CacheManager

        session_mock = AsyncMock()
        cache_mock = AsyncMock()
        entity_manager = EntityManager(session_mock)
        cache_manager = EntityManager(cache_mock)

        album_repository = AlbumRepository(entity_manager, cache_manager, Album)

        self.assertTrue(isinstance(album_repository.entity_manager, EntityManager))  # noqa E501
        self.assertTrue(isinstance(album_repository.cache_manager, CacheManager))  # noqa E501
        self.assertEqual(album_repository.entity_class, Album)

    async def test__album_repository_insert(self):
        album_mock = MagicMock()
        await self.album_repository.insert(album_mock)

        self.entity_manager_mock.insert.assert_called_once()
        self.entity_manager_mock.insert.assert_called_with(album_mock, commit=True)  # noqa E501

        self.cache_manager_mock.set.assert_called_once()
        self.cache_manager_mock.set.assert_called_with(album_mock)

    async def test__album_repository_insert_commit_true(self):
        album_mock = MagicMock()
        await self.album_repository.insert(album_mock, commit=True)

        self.entity_manager_mock.insert.assert_called_once()
        self.entity_manager_mock.insert.assert_called_with(album_mock, commit=True)  # noqa E501

        self.cache_manager_mock.set.assert_called_once()
        self.cache_manager_mock.set.assert_called_with(album_mock)

    async def test__album_repository_insert_commit_false(self):
        album_mock = MagicMock()
        await self.album_repository.insert(album_mock, commit=False)

        self.entity_manager_mock.insert.assert_called_once()
        self.entity_manager_mock.insert.assert_called_with(album_mock, commit=False)  # noqa E501

        self.cache_manager_mock.set.assert_not_called()

    async def test__album_repository_select_album_id_cache_none(self):
        album_mock = MagicMock()
        self.cache_manager_mock.get.return_value = None
        self.entity_manager_mock.select.return_value = album_mock

        result = await self.album_repository.select(album_id=123)
        self.assertEqual(result, album_mock)
        self.cache_manager_mock.get.assert_called_once()
        self.cache_manager_mock.get.assert_called_with(Album, 123)
        self.entity_manager_mock.select.assert_called_once()
        self.entity_manager_mock.select.assert_called_with(Album, 123)
        self.cache_manager_mock.set.assert_called_once()
        self.cache_manager_mock.set.assert_called_with(album_mock)

    async def test__album_repository_select_album_id_cache_exists(self):
        album_mock = MagicMock()
        self.cache_manager_mock.get.return_value = album_mock

        result = await self.album_repository.select(album_id=123)
        self.assertEqual(result, album_mock)
        self.cache_manager_mock.get.assert_called_once()
        self.cache_manager_mock.get.assert_called_with(Album, 123)
        self.entity_manager_mock.select.assert_not_called()
        self.cache_manager_mock.set.assert_called_once()
        self.cache_manager_mock.set.assert_called_with(album_mock)

    async def test__album_repository_select_kwargs(self):
        kwargs = {"key1": "value1", "key2": "value2"}
        album_mock = MagicMock()
        self.entity_manager_mock.select_by.return_value = album_mock

        result = await self.album_repository.select(**kwargs)
        self.assertEqual(result, album_mock)
        self.cache_manager_mock.get.assert_not_called()
        self.entity_manager_mock.select_by.assert_called_once()
        self.entity_manager_mock.select_by.assert_called_with(Album, **kwargs)
        self.cache_manager_mock.set.assert_called_once()
        self.cache_manager_mock.set.assert_called_with(album_mock)


if __name__ == "__main__":
    unittest.main()
