import logging
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import List, Optional

from aiohttp import ClientResponseError

from ider.models.ider_track import IderTrack

logger = logging.getLogger(__name__)


class AcoustIDClient:

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

    async def post(self, url: str, data: None | dict =None):
        async with self._session.post(url, json=data) as resp:
            result = await self._get_response(resp)
            return result

    async def push_fingerprints(self, tracks: List[IderTrack]) -> bool:
        url = f"{self._addr}/v1/priv/prod-music"
        for track in tracks:
            assert track.fingerprint
            payload = {
                "fingerprint": track.fingerprint,
                "metadata": {
                    "title": track.title,
                    "artist": track.artist,
                    "mb_id": track.musicbrainz_id
                },
            }
            response = await self.post(url, data=payload)
            print(response)


    async def get_paths_of_users_tracks(self, user: str) -> List[IderTrack]:
        url = f"{self._addr}/item/query/user:{user}"
        response = await self.get(url)
        assert len(response['results'])
        results = response['results']
        paths = []
        for result in results:
            path = Path(result['path'].lstrip(self._base_path_to_remove))
            id = result['id']
            assert path.exists()
            paths.append(IderTrack(file_path=path, beets_id=id))
        return paths
