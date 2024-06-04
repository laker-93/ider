import logging
from tempfile import TemporaryDirectory

from ider.clients.acoustid_client import AcoustIDClient
from ider.controllers.db_controller import DbController
from ider.controllers.ffmpeg_controller import FFMPEGController
from ider.controllers.fpcalc_controller import FPCalcController
from ider.models.ider_track import IderTrack

logger = logging.getLogger(__name__)


class MatchOrchestrator:
    def __init__(
            self,
            ffmpeg_controller: FFMPEGController,
            fpcalc_controller: FPCalcController,
            acoustid_client: AcoustIDClient,
            db_controller: DbController
    ):
        self._ffmpeg_controller = ffmpeg_controller
        self._fpcalc_controller = fpcalc_controller
        self._acoustid_client = acoustid_client
        self._db_controller = db_controller

    async def match(self, track: IderTrack):
        with TemporaryDirectory() as tmp_dir:
            output_path = tmp_dir / track.title
            start = 0
            window_size = 15
            await self._ffmpeg_controller.make_segment(start, track.file_path, window_size, output_path)
            fingerprint = await self._fpcalc_controller.calculate_fingerprint(output_path)
            match = await self._acoustid_client.search_for_match(fingerprint)
            n_segments_saved = 0
            while (start + window_size) < track.duration:
                if match:
                    logger.info("saving segment to db")
                    self._db_controller.upload_track_segment(
                        track.beets_id, start, start + window_size, match['mbid'], match['artist'], match['title']
                    )
                    n_segments_saved += 1
                    start += window_size
                else:
                    start += 1
                await self._ffmpeg_controller.make_segment(start, track.file_path, window_size, output_path)
                fingerprint = await self._fpcalc_controller.calculate_fingerprint(output_path)
                match = await self._acoustid_client.search_for_match(fingerprint)
        logger.info("saved %d segments to db", n_segments_saved)
