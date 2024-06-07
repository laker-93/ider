import logging
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import List, AsyncIterator

import aiohttp
from aiohttp import ClientResponseError

from ider.models.ider_track import IderTrack

logger = logging.getLogger(__name__)


class BeetsClient:

    def __init__(self, addr: str, public_addr: str, session):
        self._addr = addr
        self._public_addr = public_addr
        self._session = session

    @staticmethod
    async def _get_response(resp):
        try:
            # disable the content type check incase the server's response is not json encoded
            result = await resp.json(content_type=None)
        except JSONDecodeError:
            # response cannot be decoded in to json, try read the raw bytes.
            result = await resp.read()
            result = result.decode()
        if resp.status != 200:
            error_msg = f"failed request with detail {result} and response {resp}"
            logger.error(error_msg)
            raise ClientResponseError(
                resp.request_info,
                resp.history,
                status=resp.status,
                message=result,
                headers=resp.headers,
            )
        return result

    async def get(self, url: str, headers=None):
        async with self._session.get(url, headers=headers) as resp:
            result = await self._get_response(resp)
            return result

    async def get_path_of_public_user_track(self, beet_id: int, user: str) -> IderTrack:
        url = f"{self._public_addr}/item/query/id:{beet_id}/user:{user}"
        response = await self.get(url)
        assert len(response['results']) == 1
        result = response['results'][0]
        path = Path(result['path'])
        title = result['title']
        artist = result['artist']
        mbid = result['mb_trackid']
        duration = result['length']
        logger.info('setting path of public user track %s - %s to %s', artist, title, path)
        assert path.exists()
        return IderTrack(
            file_path=path, beets_id=beet_id, musicbrainz_id=mbid, title=title, artist=artist, duration=duration
        )

    async def download_users_tracks(self, base_path: Path, user: str) -> AsyncIterator[IderTrack]:
        url = f"{self._addr}/item/query/user:{user}"
        response = await self.get(url)
        assert len(response['results']), f'no results found for user {user}. Beets response: {response}'
        results = response['results']
        logger.info("found %d tracks for user %s", len(results), user)
        for result in results:
            id = result['id']
            url = f'{self._addr}/item/{id}/file'
            title = result['title']
            artist = result['artist']
            mbid = result['mb_trackid']
            duration = result['length']
            file_path = base_path / Path(f"{user}/{artist}-{title}-{mbid}")
            logger.info("downloading track %s - %s to location %s", artist, title, file_path)
            await self._download(file_path, url)
            yield IderTrack(
                file_path=file_path, beets_id=id, musicbrainz_id=mbid, title=title, artist=artist, duration=duration
            )

    @staticmethod
    async def _download(file_path, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    file_path.parent.mkdir(exist_ok=True)
                    file_path.touch()
                    with open(file_path, 'wb') as fd:
                        async for chunk in resp.content.iter_chunked(50):
                            fd.write(chunk)
