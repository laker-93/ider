import json
import asyncio
import logging
import subprocess
from asyncio import create_subprocess_shell
from pathlib import Path
from typing import List

from ider.models.ider_track import IderTrack
from ider.utils.run_sub_cmd import run_sub_cmd

logger = logging.getLogger(__name__)


class FPCalcController:
    def __init__(self):
        self._cmd = "fpcalc -json '{file_path}'"

    async def calculate_fingerprint(self, file_path: Path) -> str:
        cmd = self._cmd.format(file_path=file_path)
        try:
            output = await run_sub_cmd(cmd)
            result = json.loads(output)
        except RuntimeError:
            msg = f'following error occurred attempting to fpcalc {file_path}:'
            logger.exception(msg)
            raise
        else:
            return result['fingerprint']
