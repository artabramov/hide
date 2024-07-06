"""Entity manager tests."""

import unittest
import asynctest
from unittest.mock import MagicMock, AsyncMock, patch  # , call


class EntityManagerTestCase(asynctest.TestCase):
    """Entity manager test case."""

    async def setUp(self):
        """Set up before each test."""
        from app.managers.entity_manager import EntityManager

        self.session_mock = AsyncMock()
        self.entity_manager = EntityManager(self.session_mock)

    async def tearDown(self):
        """Tear down after each test."""
        del self.session_mock
        del self.entity_manager

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert(self, commit_mock, flush_mock):
        """Insert entity into database when flush and commit by default."""
        entity_mock = MagicMock()
        await self.entity_manager.insert(entity_mock)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(entity_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert_flush_true(self, commit_mock,
                                                     flush_mock):
        """Insert entity into database when flush is true."""
        entity_mock = MagicMock()
        await self.entity_manager.insert(entity_mock, flush=True)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(entity_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert_flush_false(self, commit_mock,
                                                      flush_mock):
        """Insert entity into database when flush is false."""
        entity_mock = MagicMock()
        await self.entity_manager.insert(entity_mock, flush=False)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(entity_mock)
        flush_mock.assert_not_called()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert_commit_true(self, commit_mock,
                                                      flush_mock):
        """Insert entity into database when commit is true."""
        entity_mock = MagicMock()
        await self.entity_manager.insert(entity_mock, commit=True)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(entity_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert_commit_false(self, commit_mock,
                                                       flush_mock):
        """Insert entity into database when commit is false."""
        entity_mock = MagicMock()
        await self.entity_manager.insert(entity_mock, commit=False)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(entity_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    # @patch("app.managers.entity_manager.EntityManager.flush")
    # @patch("app.managers.entity_manager.EntityManager.commit")
    # async def test__entity_manager_insert_all(self, commit_mock, flush_mock):
    #     """Insert entities into database when flush and commit by default."""
    #     entity_mocks = [MagicMock(), MagicMock()]
    #     await self.entity_manager.insert_all(entity_mocks)

    #     self.session_mock.add_all.assert_called_once()
    #     self.session_mock.add_all.assert_called_with(entity_mocks)
    #     flush_mock.assert_called_once()
    #     commit_mock.assert_not_called()

    # @patch("app.managers.entity_manager.EntityManager.flush")
    # @patch("app.managers.entity_manager.EntityManager.commit")
    # async def test__entity_manager_insert_all_flush_true(self, commit_mock,
    #                                                      flush_mock):
    #     """Insert entities into database when flush is true."""
    #     entity_mocks = [MagicMock(), MagicMock()]
    #     await self.entity_manager.insert_all(entity_mocks, flush=True)

    #     self.session_mock.add_all.assert_called_once()
    #     self.session_mock.add_all.assert_called_with(entity_mocks)
    #     flush_mock.assert_called_once()
    #     commit_mock.assert_not_called()

    # @patch("app.managers.entity_manager.EntityManager.flush")
    # @patch("app.managers.entity_manager.EntityManager.commit")
    # async def test__entity_manager_insert_all_flush_false(self, commit_mock,
    #                                                       flush_mock):
    #     """Insert entities into database when flush is false."""
    #     entity_mocks = [MagicMock(), MagicMock()]
    #     await self.entity_manager.insert_all(entity_mocks, flush=False)

    #     self.session_mock.add_all.assert_called_once()
    #     self.session_mock.add_all.assert_called_with(entity_mocks)
    #     flush_mock.assert_not_called()
    #     commit_mock.assert_not_called()

    # @patch("app.managers.entity_manager.EntityManager.flush")
    # @patch("app.managers.entity_manager.EntityManager.commit")
    # async def test__entity_manager_insert_all_commit_true(self, commit_mock,
    #                                                       flush_mock):
    #     """Insert entities into database when commit is true."""
    #     entity_mocks = [MagicMock(), MagicMock()]
    #     await self.entity_manager.insert_all(entity_mocks, commit=True)

    #     self.session_mock.add_all.assert_called_once()
    #     self.session_mock.add_all.assert_called_with(entity_mocks)
    #     flush_mock.assert_called_once()
    #     commit_mock.assert_called_once()

    # @patch("app.managers.entity_manager.EntityManager.flush")
    # @patch("app.managers.entity_manager.EntityManager.commit")
    # async def test__entity_manager_insert_all_commit_false(self, commit_mock,
    #                                                        flush_mock):
    #     """Insert entities into database when commit is false."""
    #     entity_mocks = [MagicMock(), MagicMock()]
    #     await self.entity_manager.insert_all(entity_mocks, commit=False)

    #     self.session_mock.add_all.assert_called_once()
    #     self.session_mock.add_all.assert_called_with(entity_mocks)
    #     flush_mock.assert_called_once()
    #     commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.select")
    async def test__entity_manager_select(self, select_mock):
        """Select entity from database."""
        entity_mock = MagicMock(id=123)
        class_mock = MagicMock(id=123)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = entity_mock # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        result = await self.entity_manager.select(class_mock, 123)

        self.assertEqual(result, entity_mock)
        select_mock.assert_called_once()
        select_mock.assert_called_with(class_mock)
        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(True)
        select_mock.return_value.where.return_value.limit.assert_called_once()
        select_mock.return_value.where.return_value.limit.assert_called_with(1)
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__entity_manager_select_by(self, select_mock, where_mock):
        """Select entity from database by attribute."""
        entity_mock = MagicMock(key="dummy")
        class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = entity_mock # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        result = await self.entity_manager.select_by(class_mock,
                                                     key__eq="dummy")

        self.assertEqual(result, entity_mock)
        select_mock.assert_called_once()
        select_mock.assert_called_with(class_mock)
        where_mock.assert_called_once()
        where_mock.assert_called_with(class_mock, key__eq="dummy")
        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(*where_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.limit.assert_called_once()
        select_mock.return_value.where.return_value.limit.assert_called_with(1)
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update(self, commit_mock, flush_mock):
        """Update entity in database when flush and commit by default."""
        entity_mock = MagicMock()
        await self.entity_manager.update(entity_mock)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(entity_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update_flush_true(self, commit_mock,
                                                     flush_mock):
        """Update entity in database when flush is true."""
        entity_mock = MagicMock()
        await self.entity_manager.update(entity_mock, flush=True)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(entity_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update_flush_false(self, commit_mock,
                                                      flush_mock):
        """Update entity in database when flush is false."""
        entity_mock = MagicMock()
        await self.entity_manager.update(entity_mock, flush=False)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(entity_mock)
        flush_mock.assert_not_called()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update_commit_true(self, commit_mock,
                                                      flush_mock):
        """Update entity in database when commit is true."""
        entity_mock = MagicMock()
        await self.entity_manager.update(entity_mock, commit=True)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(entity_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update_commit_false(self, commit_mock,
                                                       flush_mock):
        """Update entity in database when commit is false."""
        entity_mock = MagicMock()
        await self.entity_manager.update(entity_mock, commit=False)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(entity_mock)
        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_delete(self, commit_mock):
        """Delete entity from database when default commit."""
        entity_mock = MagicMock()
        await self.entity_manager.delete(entity_mock)

        self.session_mock.delete.assert_called_once()
        self.session_mock.delete.assert_called_with(entity_mock)
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_delete_commit_true(self, commit_mock):
        """Delete entity from database when commit is true."""
        entity_mock = MagicMock()
        await self.entity_manager.delete(entity_mock, commit=True)

        self.session_mock.delete.assert_called_once()
        self.session_mock.delete.assert_called_with(entity_mock)
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_delete_commit_false(self, commit_mock):
        """Delete entity from database when commit is false."""
        entity_mock = MagicMock()
        await self.entity_manager.delete(entity_mock, commit=False)

        self.session_mock.delete.assert_called_once()
        self.session_mock.delete.assert_called_with(entity_mock)
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__exists_true(self, select_mock, where_mock):
        """Check if entity exists in database."""
        entity_mock = MagicMock()
        class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = entity_mock # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}
        result = await self.entity_manager.exists(class_mock, **kwargs)

        self.assertTrue(result)
        select_mock.assert_called_once()
        select_mock.assert_called_with(class_mock)
        where_mock.assert_called_once()
        where_mock.assert_called_with(class_mock, **kwargs)
        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(*where_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.limit.assert_called_once()
        select_mock.return_value.where.return_value.limit.assert_called_with(1)
        self.session_mock.execute.assert_called_once()
        self.session_mock.execute.assert_called_with(select_mock.return_value.where.return_value.limit.return_value) # noqa E501
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__exists_false(self, select_mock, where_mock):
        """Check if entity is not exist in database."""
        class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}
        result = await self.entity_manager.exists(class_mock, **kwargs)

        self.assertFalse(result)
        select_mock.assert_called_once()
        select_mock.assert_called_with(class_mock)
        where_mock.assert_called_once()
        where_mock.assert_called_with(class_mock, **kwargs)
        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(*where_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.limit.assert_called_once()
        select_mock.return_value.where.return_value.limit.assert_called_with(1)
        self.session_mock.execute.assert_called_once()
        self.session_mock.execute.assert_called_with(select_mock.return_value.where.return_value.limit.return_value) # noqa E501
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._limit")
    @patch("app.managers.entity_manager.EntityManager._offset")
    @patch("app.managers.entity_manager.EntityManager._order_by")
    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__select_all(self, select_mock, where_mock, order_by_mock,
                               offset_mock, limit_mock):
        """Select all entities from database."""
        entity_mock = MagicMock()
        class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.all.return_value = [entity_mock] # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy", "order_by": "id", "order": "asc",
                  "offset": 1, "limit": 2}
        result = await self.entity_manager.select_all(class_mock, **kwargs)

        self.assertListEqual(result, [entity_mock])
        select_mock.assert_called_once()
        select_mock.assert_called_with(class_mock)
        where_mock.assert_called_once()
        where_mock.assert_called_with(class_mock, **kwargs)
        order_by_mock.assert_called_once()
        order_by_mock.assert_called_with(class_mock, **kwargs)
        offset_mock.assert_called_once()
        offset_mock.assert_called_with(**kwargs)
        limit_mock.assert_called_once()
        limit_mock.assert_called_with(**kwargs)
        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(*where_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.assert_called_once() # noqa E501
        select_mock.return_value.where.return_value.order_by.assert_called_with(order_by_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.assert_called_once() # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.assert_called_with(offset_mock.return_value) # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.assert_called_once() # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.assert_called_with(limit_mock.return_value) # noqa E501
        async_result_mock.unique.return_value.scalars.return_value.all.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__count_all(self, select_mock, func_mock, where_mock):
        """Count entities in database."""
        class_mock = MagicMock(id=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}
        result = await self.entity_manager.count_all(class_mock, **kwargs)

        self.assertEqual(result, 123)
        func_mock.count.assert_called_once()
        func_mock.count.assert_called_with(class_mock.id)
        where_mock.assert_called_once()
        where_mock.assert_called_with(class_mock, **kwargs)
        select_mock.assert_called_once()
        select_mock.assert_called_with(func_mock.count.return_value)
        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(*where_mock.return_value) # noqa E501
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__count_all_none(self, select_mock, func_mock, where_mock):
        """Count entities in database when result is none."""
        class_mock = MagicMock(id=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}
        result = await self.entity_manager.count_all(class_mock, **kwargs)

        self.assertEqual(result, 0)
        func_mock.count.assert_called_once()
        func_mock.count.assert_called_with(class_mock.id)
        where_mock.assert_called_once()
        where_mock.assert_called_with(class_mock, **kwargs)
        select_mock.assert_called_once()
        select_mock.assert_called_with(func_mock.count.return_value)
        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(*where_mock.return_value) # noqa E501
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__sum_all(self, select_mock, func_mock, where_mock):
        """Summarize attribute of entity in database."""
        class_mock = MagicMock(name="dummy", number=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}
        result = await self.entity_manager.sum_all(class_mock, "number",
                                                   **kwargs)

        self.assertEqual(result, 123)
        func_mock.sum.assert_called_once()
        func_mock.sum.assert_called_with(class_mock.number)
        where_mock.assert_called_once()
        where_mock.assert_called_with(class_mock, **kwargs)
        select_mock.assert_called_once()
        select_mock.assert_called_with(func_mock.sum.return_value)
        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(
            *where_mock.return_value)
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__sum_all_none(self, select_mock, func_mock, where_mock):
        """Summarize attribute of entity in database when result is none."""
        class_mock = MagicMock(name="dummy", number=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}
        result = await self.entity_manager.sum_all(class_mock, "number",
                                                   **kwargs)

        self.assertEqual(result, 0)
        func_mock.sum.assert_called_once()
        func_mock.sum.assert_called_with(class_mock.number)
        where_mock.assert_called_once()
        where_mock.assert_called_with(class_mock, **kwargs)
        select_mock.assert_called_once()
        select_mock.assert_called_with(func_mock.sum.return_value)
        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(*where_mock.return_value) # noqa E501
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    # @patch("app.managers.entity_manager.EntityManager.delete")
    # @patch("app.managers.entity_manager.EntityManager.select_all")
    # async def test__delete_all_commit_true(self, select_all_mock,
    #                                          delete_mock):
    #     """Delete all entities from database when commit is true."""
    #     class_mock = MagicMock()
    #     entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
    #     select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]
    #     await self.entity_manager.delete_all(class_mock, 2, commit=True,
    #                                          name__eq="dummy")

    #     self.assertEqual(select_all_mock.call_count, 3)
    #     self.assertListEqual(select_all_mock.call_args_list, [
    #         call(class_mock, name__eq="dummy", order_by="id", order="asc",
    #              offset=0, limit=2),
    #         call(class_mock, name__eq="dummy", order_by="id", order="asc",
    #              offset=2, limit=2),
    #         call(class_mock, name__eq="dummy", order_by="id", order="asc",
    #              offset=4, limit=2),
    #     ])
    #     self.assertEqual(delete_mock.call_count, 3)
    #     self.assertListEqual(delete_mock.call_args_list, [
    #         call(entity_1, commit=True),
    #         call(entity_2, commit=True),
    #         call(entity_3, commit=True),
    #     ])

    # @patch("app.managers.entity_manager.EntityManager.delete")
    # @patch("app.managers.entity_manager.EntityManager.select_all")
    # async def test__delete_all_commit_false(self, select_all_mock,
    #                                           delete_mock):
    #     """Delete all entities from database when commit is false."""
    #     class_mock = MagicMock()
    #     entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
    #     select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]
    #     await self.entity_manager.delete_all(class_mock, 2, commit=False,
    #                                          name__eq="dummy")

    #     self.assertEqual(select_all_mock.call_count, 3)
    #     self.assertListEqual(select_all_mock.call_args_list, [
    #         call(class_mock, name__eq="dummy", order_by="id", order="asc",
    #              offset=0, limit=2),
    #         call(class_mock, name__eq="dummy", order_by="id", order="asc",
    #              offset=2, limit=2),
    #         call(class_mock, name__eq="dummy", order_by="id", order="asc",
    #              offset=4, limit=2),
    #     ])
    #     self.assertEqual(delete_mock.call_count, 3)
    #     self.assertListEqual(delete_mock.call_args_list, [
    #         call(entity_1, commit=False),
    #         call(entity_2, commit=False),
    #         call(entity_3, commit=False),
    #     ])

    # @patch("app.managers.entity_manager.text")
    # async def test__execute(self, text_mock):
    #     """Execute custom query."""
    #     sql = "SELECT 1;"
    #     result = await self.entity_manager.execute(sql)

    #     self.assertEqual(result, self.session_mock.execute.return_value)
    #     text_mock.assert_called_once()
    #     text_mock.assert_called_with(sql)
    #     self.session_mock.execute.assert_called_once()
    #     self.session_mock.execute.assert_called_with(text_mock.return_value)

    async def test__flush(self):
        """Flush changes."""
        await self.entity_manager.flush()
        self.session_mock.flush.assert_called_once()

    async def test__commit(self):
        """Commit transaction."""
        await self.entity_manager.commit()
        self.session_mock.commit.assert_called_once()

    async def test__rollback(self):
        """Rollback transaction."""
        await self.entity_manager.rollback()
        self.session_mock.rollback.assert_called_once()

    async def test__where(self):
        """Build where statement."""
        (in_mock, eq_mock, not_mock, gte_mock, lte_mock, gt_mock, lt_mock,
         like_mock, ilike_mock) = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(),
            MagicMock(), MagicMock(), MagicMock(), MagicMock())
        column_mock = MagicMock(
            in_=in_mock, __eq__=eq_mock, __ne__=not_mock, __ge__=gte_mock,
            __le__=lte_mock, __gt__=gt_mock, __lt__=lt_mock, like=like_mock,
            ilike=ilike_mock)
        class_mock = MagicMock(column=column_mock)
        kwargs = {
            "column__in": [1, 2],
            "column__eq": 3,
            "column__not": 4,
            "column__gte": 5,
            "column__lte": 6,
            "column__gt": 7,
            "column__lt": 8,
            "column__like": "dummy",
            "column__ilike": "dummy",
        }
        result = self.entity_manager._where(class_mock, **kwargs)

        self.assertListEqual(result, [
            in_mock.return_value,
            eq_mock.return_value,
            not_mock.return_value,
            gte_mock.return_value,
            lte_mock.return_value,
            gt_mock.return_value,
            lt_mock.return_value,
            like_mock.return_value,
            ilike_mock.return_value,
        ])
        in_mock.assert_called_once()
        in_mock.assert_called_with(kwargs["column__in"])
        eq_mock.assert_called_once()
        eq_mock.assert_called_with(kwargs["column__eq"])
        not_mock.assert_called_once()
        not_mock.assert_called_with(kwargs["column__not"])
        gte_mock.assert_called_once()
        gte_mock.assert_called_with(kwargs["column__gte"])
        lte_mock.assert_called_once()
        lte_mock.assert_called_with(kwargs["column__lte"])
        gt_mock.assert_called_once()
        gt_mock.assert_called_with(kwargs["column__gt"])
        lt_mock.assert_called_once()
        lt_mock.assert_called_with(kwargs["column__lt"])
        like_mock.assert_called_once()
        like_mock.assert_called_with("%" + kwargs["column__like"] + "%")
        ilike_mock.assert_called_once()
        ilike_mock.assert_called_with("%" + kwargs["column__ilike"] + "%")

    @patch("app.managers.entity_manager.asc")
    async def test__order_by_asc(self, asc_mock):
        """Build order by statement when order is asc."""
        column_mock = MagicMock()
        class_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "asc"}
        result = self.entity_manager._order_by(class_mock, **kwargs)

        self.assertEqual(result, asc_mock.return_value)
        asc_mock.assert_called_once()
        asc_mock.assert_called_with(column_mock)

    @patch("app.managers.entity_manager.desc")
    async def test__order_by_desc(self, desc_mock):
        """Build order by statement when order is desc."""
        column_mock = MagicMock()
        class_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "desc"}
        result = self.entity_manager._order_by(class_mock, **kwargs)

        self.assertEqual(result, desc_mock.return_value)
        desc_mock.assert_called_once()
        desc_mock.assert_called_with(column_mock)

    async def test__offset(self):
        """Build offset statement."""
        kwargs = {"offset": 123}
        result = self.entity_manager._offset(**kwargs)
        self.assertEqual(result, 123)

    async def test__limit(self):
        """Build limit statement."""
        kwargs = {"limit": 123}
        result = self.entity_manager._limit(**kwargs)
        self.assertEqual(result, 123)


if __name__ == '__main__':
    unittest.main()
