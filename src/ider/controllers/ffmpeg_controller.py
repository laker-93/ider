import logging
from pathlib import Path

from ider.utils.run_sub_cmd import run_sub_cmd

logger = logging.getLogger(__name__)

class FFMPEGController:
    async def make_segment(self, start: int, filepath: Path, window_size: int, output_path: Path):
        # cmd = 'ffmpeg -ss 640 -i ~/Music/mixes/REC001.WAV -t 20 -c copy updown.wav'
        cmd = f"ffmpeg -ss {start} -i '{filepath.absolute()}' -t {window_size} -c copy '{output_path}'"
        logger.info('running ffmpeg on filepath %s', filepath.absolute())
        await run_sub_cmd(cmd, supress_exception=True)
