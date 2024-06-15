import json
import logging
from typing import Optional

from tinydb import TinyDB, Query

logger = logging.getLogger(__name__)


class DbController:
    def __init__(self, db: TinyDB, app_env: str):
        self._db = db
        self._app_env = app_env
        self._raw_match_schema = ('track_id', 'start', 'end', 'mbid', 'artist', 'title', 'window_start', 'window_size', 'segment_number')
        self._track_segment_ids_schema = ('track_id', 'start', 'end', 'mbid', 'artist', 'title')

    def upload_raw_match(self, track_id: int, start: float, end: float, mbid: str, artist: str, title: str, window_start: int, window_size: int, segment_number: int):
        table = self._db.table('raw_match_table')
        table.insert(
            dict(zip(self._raw_match_schema, (track_id, start, end, mbid, artist, title, window_start, window_size, segment_number)))
        )

    def upload_segment(self, track_id: int, start: float, end: float, mbid: str, artist: str, title: str):
        table = self._db.table('track_segment_ids_table')
        table.insert(
            dict(zip(self._raw_match_schema, (track_id, start, end, mbid, artist, title)))
        )

    def get_ids_by_time(self, track_id: int, cur_time: int) -> Optional[str]:
        Segment = Query()
        segment_table = self._db.table('track_segment_ids_table')
        results = segment_table.search(
            (Segment.track_id == track_id) & (Segment.start <= cur_time) & (Segment.end > cur_time))
        if results:
            matches = []
            for result in results:
                mbid = result['mbid']
                artist = result['artist']
                title = result['title']
                matches.append(
                    {
                        'mbid': mbid,
                        'artist': artist,
                        'title': title,
                    }
                )
            return json.dumps(matches)
        else:
            logger.info(f'no matching segment found for track id {track_id} at time {cur_time}')
            return None

    def get_tracklist(self, track_id: int) -> Optional[list[dict]]:
        Segment = Query()
        segment_table = self._db.table('track_segment_ids_table')
        results = segment_table.search(
            (Segment.track_id == track_id)
        )
        if results:
            results.sort(key=lambda r: r['start'])
            return results
        else:
            logger.info(f'no segments found for track id {track_id}')
            return None
