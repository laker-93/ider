import logging
from json import JSONDecodeError
from typing import AsyncIterator

from aiohttp import ClientResponseError

from ider.models.ider_track import IderTrack
from ider.models.match import Match

logger = logging.getLogger(__name__)

class DuplicateFingerprint(Exception):
    pass

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
            if result['error']['type'] == 'duplicate':
                raise DuplicateFingerprint()
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

    async def push_fingerprints(self, track: IderTrack) -> bool:
        url = f"{self._addr}/v1/priv/prod-music"
        assert track.fingerprint
        result = False
        payload = {
            "fingerprint": track.fingerprint,
            "metadata": {
                "title": track.title,
                "artist": track.artist,
                "mb_id": track.musicbrainz_id
            },
        }
        try:
            await self.post(url, data=payload)
        except DuplicateFingerprint:
            logger.info(f'The fingerprint of track %s is already in the acoustid db', track)
        else:
            result = True
        return result

    async def search_for_match(self, fingerprint: str, window_size: float) -> AsyncIterator[None | Match]:
        url = f"{self._addr}/v1/priv/prod-music/_search"
        params = {
            "stream": True,
            "fingerprint": fingerprint
        }
        match = await self.post(url, data=params)
        match_results = match.get('results')
        logger.debug(f'got match results {match_results}')
        for result in match_results:
            metadata = result.get('metadata')
            if not metadata:
                logger.warning('no metadata entry found in result %s', result)
                continue
            match = result.get('match')
            if not match:
                logger.warning('no match entry found in result %s', result)
                continue

            mb_id = metadata['mb_id']
            artist = metadata['artist']
            title = metadata['title']
            offset = match['position_in_query']
            duration = match['duration']
            yield Match(
                mb_id=mb_id,
                artist=artist,
                title=title,
                duration=duration,
                window_size=window_size,
                offset=offset
            )
