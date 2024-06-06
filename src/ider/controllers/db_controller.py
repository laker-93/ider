import logging
from collections import defaultdict
from typing import Optional, Tuple, List, Dict

from tinydb import TinyDB, Query

logger = logging.getLogger(__name__)


class DbController:
    def __init__(self, db: TinyDB, app_env: str):
        self._db = db
        self._app_env = app_env
        self._track_segment_ids_seconds_schema = ('track_id', 'start', 'end', 'mbid', 'artist', 'title', 'window_start', 'window_size', 'segment_number')

    def upload_track_segment(self, track_id: int, start: float, end: float, mbid: str, artist: str, title: str, window_start: int, window_size: int, segment_number: int):
        segment_table = self._db.table('track_segment_ids_table')
        segment_table.insert(
            dict(zip(self._track_segment_ids_seconds_schema, (track_id, start, end, mbid, artist, title, window_start, window_size, segment_number)))
        )

    def get_ids_by_time(self, track_id: int, cur_time: int) -> Optional[Dict[Tuple[Optional[str], str, str], int]]:
        Segment = Query()
        segment_table = self._db.table('track_segment_ids_table')
        results = segment_table.search(
            (Segment.track_id == track_id) & (Segment.start <= cur_time) & (Segment.end > cur_time))
        if results:
            match_counts = defaultdict(int)
            for result in results:
                mbid = result['mbid']
                artist = result['artist']
                title = result['title']
                key = mbid, artist, title
                match_counts[key] += 1
            return match_counts
        else:
            logger.info(f'no matching segment found for track id {track_id} at time {cur_time}')
            return None
