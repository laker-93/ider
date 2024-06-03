import json
import asyncio
import logging
import subprocess
from asyncio import create_subprocess_shell
from pathlib import Path
from typing import List

from ider.models.ider_track import IderTrack

logger = logging.getLogger(__name__)


class FPCalcController:

    @staticmethod
    async def _calculate_fpcalc(file_path: Path) -> str:
        proc = await asyncio.create_subprocess_shell(
            f"fpcalc -json '{file_path}'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stderr:
            msg = f'error occurred attempting to fpcalc {file_path}: stderr'
            logger.exception(msg)
            raise RuntimeError(msg)
        logger.info(f'lajp got fingerprint: {stdout.decode()}')
        fpcalc_result = json.loads(stdout.decode())
        return fpcalc_result['fingerprint']

    async def calculate_fpcalc(self, tracks: List[IderTrack]):
        for track in tracks:
            track.fingerprint = await self._calculate_fpcalc(track.file_path)
