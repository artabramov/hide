import asynctest
from unittest.mock import AsyncMock, patch, call
from app.managers.file_manager import FileManager
from app.config import get_config

cfg = get_config()


class CacheManagerTestCase(asynctest.TestCase):
    """Test case for FileManager class."""

    async def setUp(self):
        """Set up the test case environment."""
        pass

    async def tearDown(self):
        """Clean up the test case environment."""
        pass

    @patch("app.managers.file_manager.aiofiles")
    async def test__upload(self, aiofiles_mock):
        file_mock = AsyncMock()
        chunk1, chunk2 = b"data1", b"data2"
        file_mock.read.side_effect = [chunk1, chunk2, None]
        path = "/path"

        result = await FileManager.upload(file_mock, path)
        self.assertIsNone(result)

        aiofiles_mock.open.assert_called_once()
        aiofiles_mock.open.assert_called_with(path, mode="wb")

        self.assertEqual(file_mock.read.call_count, 3)
        self.assertListEqual(file_mock.mock_calls, [
            call.read(cfg.FILE_UPLOAD_CHUNK_SIZE),
            call.read(cfg.FILE_UPLOAD_CHUNK_SIZE),
            call.read(cfg.FILE_UPLOAD_CHUNK_SIZE),
        ])

        self.assertEqual(len(aiofiles_mock.mock_calls), 5)
        self.assertEqual(aiofiles_mock.mock_calls[0],
                         call.open(path, mode="wb"))
        self.assertEqual(aiofiles_mock.mock_calls[1],
                         call.open().__aenter__())
        self.assertEqual(aiofiles_mock.mock_calls[2],
                         call.open().__aenter__().write(chunk1))
        self.assertEqual(aiofiles_mock.mock_calls[3],
                         call.open().__aenter__().write(chunk2))
        self.assertEqual(aiofiles_mock.mock_calls[4],
                         call.open().__aexit__(None, None, None))

    @patch("app.managers.file_manager.aiofiles")
    async def test__delete_file_exists(self, aiofiles_mock):
        os_mock = AsyncMock()
        os_mock.path.isfile.return_value = True
        aiofiles_mock.os = os_mock
        path = "/path"

        result = await FileManager.delete(path)
        self.assertIsNone(result)

        os_mock.path.isfile.assert_called_once()
        os_mock.path.isfile.assert_called_with(path)

        os_mock.unlink.assert_called_once()
        os_mock.unlink.assert_called_with(path)

    @patch("app.managers.file_manager.aiofiles")
    async def test__delete_file_not_exists(self, aiofiles_mock):
        os_mock = AsyncMock()
        os_mock.path.isfile.return_value = False
        aiofiles_mock.os = os_mock
        path = "/path"

        result = await FileManager.delete(path)
        self.assertIsNone(result)

        os_mock.path.isfile.assert_called_once()
        os_mock.path.isfile.assert_called_with(path)

        os_mock.unlink.assert_not_called()

    @patch("app.managers.file_manager.aiofiles")
    async def test__write(self, aiofiles_mock):
        path = "/path"
        data = "data"

        result = await FileManager.write(path, data)
        self.assertIsNone(result)

        aiofiles_mock.open.assert_called_once()
        aiofiles_mock.open.assert_called_with(path, mode="wb")

        self.assertEqual(len(aiofiles_mock.mock_calls), 4)
        self.assertEqual(aiofiles_mock.mock_calls[0],
                         call.open(path, mode="wb"))
        self.assertEqual(aiofiles_mock.mock_calls[1],
                         call.open().__aenter__())
        self.assertEqual(aiofiles_mock.mock_calls[2],
                         call.open().__aenter__().write(data))
        self.assertEqual(aiofiles_mock.mock_calls[3],
                         call.open().__aexit__(None, None, None))

    @patch("app.managers.file_manager.aiofiles")
    async def test__read(self, aiofiles_mock):
        path = "/path"

        result = await FileManager.read(path)
        self.assertTrue(isinstance(result, AsyncMock))
        self.assertEqual(len(result.mock_calls), 1)

        aiofiles_mock.open.assert_called_once()
        aiofiles_mock.open.assert_called_with(path, mode="rb")

        self.assertEqual(len(aiofiles_mock.mock_calls), 5)
        self.assertEqual(aiofiles_mock.mock_calls[0],
                         call.open(path, mode="rb"))
        self.assertEqual(aiofiles_mock.mock_calls[1],
                         call.open().__aenter__())
        self.assertEqual(aiofiles_mock.mock_calls[2],
                         call.open().__aenter__().read())
        self.assertEqual(aiofiles_mock.mock_calls[3],
                         call.open().__aexit__(None, None, None))
        self.assertEqual(aiofiles_mock.mock_calls[2],
                         call.open().__aenter__().read())
