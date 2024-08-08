import asynctest
import unittest
from unittest.mock import MagicMock, AsyncMock
from app.repository import Repository


class RepositoryTestCase(asynctest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    async def test__repository_insert_cacheable_commit_true(self):
        entity_class_mock = MagicMock(__tablename__="entities", _cacheable=True)
        entity_mock = MagicMock()

        entity_repository = Repository(None, None, entity_class_mock)
        entity_repository.entity_manager = AsyncMock()
        entity_repository.cache_manager = AsyncMock()

        await entity_repository.insert(entity_mock, commit=True)

        entity_repository.entity_manager.insert.assert_called_once()
        entity_repository.entity_manager.insert.assert_called_with(
            entity_mock, commit=True)

        entity_repository.cache_manager.set.assert_called_once()
        entity_repository.cache_manager.set.assert_called_with(entity_mock)

    async def test__repository_insert_cacheable_commit_false(self):
        entity_class_mock = MagicMock(__tablename__="entities", _cacheable=True)
        entity_mock = MagicMock()

        entity_repository = Repository(None, None, entity_class_mock)
        entity_repository.entity_manager = AsyncMock()
        entity_repository.cache_manager = AsyncMock()

        await entity_repository.insert(entity_mock, commit=False)

        entity_repository.entity_manager.insert.assert_called_once()
        entity_repository.entity_manager.insert.assert_called_with(
            entity_mock, commit=False)

        entity_repository.cache_manager.set.assert_not_called()

    async def test__repository_insert_uncacheable_commit_true(self):
        entity_class_mock = MagicMock(__tablename__="entities",
                                      _cacheable=False)
        entity_mock = MagicMock()

        entity_repository = Repository(None, None, entity_class_mock)
        entity_repository.entity_manager = AsyncMock()
        entity_repository.cache_manager = AsyncMock()

        await entity_repository.insert(entity_mock, commit=True)

        entity_repository.entity_manager.insert.assert_called_once()
        entity_repository.entity_manager.insert.assert_called_with(
            entity_mock, commit=True)

        entity_repository.cache_manager.set.assert_not_called()

    async def test__repository_insert_uncacheable_commit_false(self):
        entity_class_mock = MagicMock(__tablename__="entities", _cacheable=False)  # noqa E501
        entity_mock = MagicMock()

        entity_repository = Repository(None, None, entity_class_mock)
        entity_repository.entity_manager = AsyncMock()
        entity_repository.cache_manager = AsyncMock()

        await entity_repository.insert(entity_mock, commit=False)

        entity_repository.entity_manager.insert.assert_called_once()
        entity_repository.entity_manager.insert.assert_called_with(
            entity_mock, commit=False)

        entity_repository.cache_manager.set.assert_not_called()

    async def test__repository_select_id_cacheable_cached(self):
        entity_class_mock = MagicMock(__tablename__="entities", _cacheable=True)
        entity_mock = MagicMock(id=123, _cacheable=True)

        entity_repository = Repository(None, None, entity_class_mock)
        entity_repository.entity_manager = AsyncMock(get=None)
        entity_repository.entity_manager.select.return_value = entity_mock
        entity_repository.cache_manager = AsyncMock()
        entity_repository.cache_manager.get.return_value = None

        result = await entity_repository.select(id=entity_mock.id)
        self.assertEqual(result, entity_mock)
        entity_repository.cache_manager.get.assert_called_once()
        entity_repository.cache_manager.get.assert_called_with(
            entity_class_mock, entity_mock.id)
        entity_repository.entity_manager.select.assert_called_once()
        entity_repository.entity_manager.select.assert_called_with(
            entity_class_mock, entity_mock.id)
        entity_repository.cache_manager.set.assert_called_once()
        entity_repository.cache_manager.set.assert_called_with(entity_mock)


if __name__ == "__main__":
    unittest.main()
