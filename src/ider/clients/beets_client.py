import logging
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import List

from aiohttp import ClientResponseError

from ider.models.ider_track import IderTrack

logger = logging.getLogger(__name__)


class BeetsClient:

    def __init__(self, addr: str, session):
        self._addr = addr
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

    async def get_path_of_user_track(self, beet_id: int, user: str) -> IderTrack:
        url = f"{self._addr}/item/query/id:{beet_id}/user:{user}"
        response = await self.get(url)
        assert len(response['results']) == 1
        results = response['results']
        path = Path(results['path'])
        title = results['title']
        artist_name = results['artist']
        mbid = results['mb_trackid']
        assert path.exists()
        return IderTrack(file_path=path, beets_id=beet_id, musicbrainz_id=mbid, title=title, artist=artist_name)

    async def get_paths_of_users_tracks(self, user: str) -> List[IderTrack]:
        url = f"{self._addr}/item/query/user:{user}"
        response = await self.get(url)
        assert len(response['results']), f'no results found for user {user}. Beets response: {response}'
        results = response['results']
        paths = []
        for result in results:
            path = Path(result['path'])
            id = result['id']
            title = result['title']
            artist = result['artist']
            mbid = result['mb_trackid']
            assert path.exists()
            paths.append(IderTrack(file_path=path, beets_id=id, musicbrainz_id=mbid, title=title, artist=artist))
        return paths
