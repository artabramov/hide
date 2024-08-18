import ffmpeg
import asyncio


class VideoHelper:

    @staticmethod
    async def freeze(src_path: str, dst_path: str):
        """Freeze frame asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, VideoHelper._freeze_sync,
                                   src_path, dst_path)

    @staticmethod
    def _freeze_sync(src_path: str, dst_path: str):
        """Synchronous version of freeze frame."""
        output = ffmpeg.input(src_path, ss=0).output(dst_path, vframes=1)
        output.overwrite_output().run(capture_stdout=True, capture_stderr=True)
