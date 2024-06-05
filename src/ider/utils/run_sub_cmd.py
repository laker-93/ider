import asyncio
import logging

logger = logging.getLogger(__name__)


async def run_sub_cmd(cmd: str, supress_exception: bool = False) -> str:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stderr and not supress_exception:
        logger.error('running cmd %s failed:', cmd)
        logger.error(stderr)
        raise RuntimeError(stderr)
    logger.debug("got output from running cmd %s: %s", cmd, stdout.decode())
    return stdout.decode()
