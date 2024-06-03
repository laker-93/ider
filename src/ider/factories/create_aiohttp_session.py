from contextlib import asynccontextmanager
from typing import Iterator

import aiohttp


@asynccontextmanager
async def init_aiohttp_session(auth=None) -> Iterator[aiohttp.ClientSession]:
    timeout = aiohttp.ClientTimeout()
    async with aiohttp.ClientSession(auth=auth, connector=aiohttp.TCPConnector(verify_ssl=False), timeout=timeout) as session:
        yield session