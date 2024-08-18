import asynctest
from unittest.mock import AsyncMock, patch, call
from app.managers.file_manager import (
    FileManager, FILE_UPLOAD_CHUNK_SIZE, FILE_COPY_CHUNK_SIZE)
from app.config import get_config

cfg = get_config()


class FileManagerTestCase(asynctest.TestCase):
    """Test case for FileManager class."""

    async def setUp(self):
        """Set up the test case environment."""
        pass

    async def tearDown(self):
        """Clean up the test case environment."""
        pass

    def test_is_image_true(self):
        """
        Verify that is_image method correctly identifies known image
        MIME types as images.
        """
        mimetypes = [
            "image/jpeg", "image/png", "image/gif", "image/bmp",
            "image/tiff", "image/webp", "image/svg+xml", "image/x-icon",
            "image/heif", "image/heic", "image/jp2", "image/avif",
            "image/apng", "image/x-tiff", "image/x-cmu-raster",
            "image/x-portable-anymap", "image/x-portable-bitmap",
            "image/x-portable-graymap", "image/x-portable-pixmap"]

        for mimetype in mimetypes:
            result = FileManager.is_image(mimetype)
            self.assertTrue(result)

    def test_is_image_false(self):
        """
        Verify that is_image method correctly identifies non-image MIME
        types as not images.
        """
        mimetypes = [
            "video/mp4", "video/avi", "video/mkv", "video/webm",
            "video/x-msvideo", "video/x-matroska", "video/quicktime"]

        for mimetype in mimetypes:
            result = FileManager.is_image(mimetype)
            self.assertFalse(result)

    def test_is_video_true(self):
        """
        Verify that is_video method correctly identifies known video
        MIME types as videos.
        """
        mimetypes = [
            "video/mp4", "video/avi", "video/mkv", "video/webm",
            "video/x-msvideo", "video/x-matroska", "video/quicktime"]

        for mimetype in mimetypes:
            result = FileManager.is_video(mimetype)
            self.assertTrue(result)

    def test_is_video_false(self):
        """
        Verify that is_video method correctly identifies non-video MIME
        types as not videos.
        """
        mimetypes = [
            "image/jpeg", "image/png", "image/gif", "image/bmp",
            "image/tiff", "image/webp", "image/jp2", "image/avif"]

        for mimetype in mimetypes:
            result = FileManager.is_video(mimetype)
            self.assertFalse(result)

    @patch("app.managers.file_manager.aiofiles")
    async def test__upload(self, aiofiles_mock):
        """
        Test the upload method to ensure it writes data to a file
        correctly.
        """
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
            call.read(FILE_UPLOAD_CHUNK_SIZE),
            call.read(FILE_UPLOAD_CHUNK_SIZE),
            call.read(FILE_UPLOAD_CHUNK_SIZE),
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
        """
        Test the delete method when the file exists to ensure it is
        removed
        ."""
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
        """
        Test the delete method when the file does not exist to ensure
        no deletion occurs.
        """
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
        """
        Test the write method to ensure data is correctly written to
        a file.
        """
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
        """
        Test the read method to ensure data is correctly read from
        a file.
        """
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

    @patch("app.managers.file_manager.cipher_suite")
    async def test__encrypt(self, cipher_suite_mock):
        """
        Test the encrypt method to ensure data is correctly encrypted.
        """
        data = "data"

        result = await FileManager.encrypt(data)
        self.assertEqual(result, cipher_suite_mock.encrypt.return_value)

        cipher_suite_mock.encrypt.assert_called_once()
        cipher_suite_mock.encrypt.assert_called_with(data)

    @patch("app.managers.file_manager.cipher_suite")
    async def test__decrypt(self, cipher_suite_mock):
        """
        Test the decrypt method to ensure data is correctly decrypted.
        """
        data = "data"

        result = await FileManager.decrypt(data)
        self.assertEqual(result, cipher_suite_mock.decrypt.return_value)

        cipher_suite_mock.decrypt.assert_called_once()
        cipher_suite_mock.decrypt.assert_called_with(data)

    @patch("app.managers.file_manager.aiofiles")
    async def test__copy(self, aiofiles_mock):
        """
        Test the copy method to ensure data is copied from source to
        destination file correctly.
        """
        src_path = "/src_path"
        dst_path = "/dst_path"

        src_context_mock = AsyncMock()
        chunk1, chunk2 = b"data1", b"data2"
        src_context_mock.__aenter__.return_value.read.side_effect = [
            chunk1, chunk2, None]

        dst_context_mock = AsyncMock()

        aiofiles_mock.open.side_effect = [src_context_mock, dst_context_mock]

        result = await FileManager.copy(src_path, dst_path)
        self.assertIsNone(result)

        self.assertEqual(aiofiles_mock.open.call_count, 2)
        self.assertListEqual(aiofiles_mock.open.call_args_list, [
            call(src_path, mode="rb"), call(dst_path, mode="wb")])

        self.assertListEqual(src_context_mock.mock_calls, [
            call.__aenter__(),
            call.__aenter__().read(FILE_COPY_CHUNK_SIZE),
            call.__aenter__().read(FILE_COPY_CHUNK_SIZE),
            call.__aenter__().read(FILE_COPY_CHUNK_SIZE),
            call.__aexit__(None, None, None)
        ])

        self.assertListEqual(dst_context_mock.mock_calls, [
            call.__aenter__(),
            call.__aenter__().write(chunk1),
            call.__aenter__().write(chunk2),
            call.__aexit__(None, None, None)
        ])
