"""
Provides functionality to freeze a frame from a video, saving the frame
as an image file. The video_freeze function runs the freezing operation
asynchronously, delegating the actual work to a synchronous helper
function _video_freeze_sync that uses FFmpeg for processing.
"""

import asyncio
import ffmpeg


def _video_freeze_sync(src_path: str, dst_path: str):
    """
    Freezes the first frame of a video and saves it as an image
    file using FFmpeg.
    """
    output = ffmpeg.input(src_path, ss=0).output(dst_path, vframes=1)
    output.overwrite_output().run(capture_stdout=True, capture_stderr=True)


async def video_freeze(src_path: str, dst_path: str):
    """
    Asynchronously freezes the first frame of a video and saves it as an
    image file by calling the synchronous _video_freeze_sync function
    within an executor.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _video_freeze_sync, src_path, dst_path)
