import logging
from typing import Optional, Tuple, List, Dict

from tinydb import TinyDB, Query

logger = logging.getLogger(__name__)


class DbController:
    def __init__(self, db: TinyDB, app_env: str):
        self._db = db
        self._app_env = app_env
        self._track_segment_ids_seconds_schema = ('track_id', 'start', 'end', 'mbid', 'artist', 'title')

    def upload_track_segment(self, track_id: int, start: float, end: float, mbid: str, artist: str, title: str):
        segment_table = self._db.table('track_segment_ids_table')
        segment_table.insert(
            dict(zip(self._track_segment_ids_seconds_schema, (track_id, start, end, mbid, artist, title)))
        )

    def get_ids_by_time(self, track_id: int, cur_time: int) -> Optional[Dict[str, List[Optional[str]]]]:
        Segment = Query()
        segment_table = self._db.table('track_segment_ids_table')
        results = segment_table.search(
            (Segment.track_id == track_id) & (Segment.start <= cur_time) & (Segment.end > cur_time))
        assert len(results) == 1 or len(
            results) == 0, f'have {len(results)} matches for mbid of track id {track_id} at time {cur_time}'
        if results:
            mbids = []
            artists = []
            titles = []
            for result in results:
                mbids.append(
                    result['mbid']
                )
                artists.append(
                    result['artist']
                )
                titles.append(
                    result['title']
                )
            return {
                'mbids': mbids,
                'artists': artists,
                'titles': titles
            }
        else:
            logger.info(f'no matching segment found for track id {track_id} at time {cur_time}')
            return None
