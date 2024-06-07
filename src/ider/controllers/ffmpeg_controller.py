import logging
from pathlib import Path

from ider.utils.run_sub_cmd import run_sub_cmd

logger = logging.getLogger(__name__)

class FFMPEGController:
    async def make_segment(self, start: int, filepath: Path, window_size: int, output_path: Path):
        # cmd = 'ffmpeg -ss 640 -i ~/Music/mixes/REC001.WAV -t 20 -c copy updown.wav'
        cmd = f"ffmpeg -y -ss {start} -i '{filepath.absolute()}' -t {window_size} -c copy '{output_path}'"
        logger.debug('running ffmpeg on %s starting at %d and ending at %d. Saving output to: %s', filepath.absolute(), start, start + window_size, output_path)
        await run_sub_cmd(cmd, supress_exception=True)
