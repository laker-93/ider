import itertools
import logging
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Optional, Iterator

from ider.clients.acoustid_client import AcoustIDClient
from ider.controllers.db_controller import DbController
from ider.controllers.ffmpeg_controller import FFMPEGController
from ider.controllers.fpcalc_controller import FPCalcController
from ider.models.ider_track import IderTrack
from ider.models.match import Match

logger = logging.getLogger(__name__)


class MatchOrchestrator:
    def __init__(
            self,
            ffmpeg_controller: FFMPEGController,
            fpcalc_controller: FPCalcController,
            acoustid_client: AcoustIDClient,
            db_controller: DbController,
            config: Dict
    ):
        self._ffmpeg_controller = ffmpeg_controller
        self._fpcalc_controller = fpcalc_controller
        self._acoustid_client = acoustid_client
        self._db_controller = db_controller
        self._n_consecutive_matches_threshold = config['n_consecutive_matches_threshold']
        self._consecutive_matches_offset_s = config['consecutive_matches_offset_s']
        self._max_n_match_attempts = config['max_n_match_attempts']
        self._window_size = config['window_size']
        self._percentage_window_covered = config['percentage_window_covered']
        self._n_rounds = config['n_rounds']

    def _confirm_match(self, potential_matches: List[Match]) -> Iterator[Match]:
        if len(potential_matches) < self._n_consecutive_matches_threshold:
            return None
        # handle the case where all matches are the same and they all roughly cover the entire window length
        # potential_matches.sort(key=lambda m: -m.duration) # sort by duration, max duration first
        # n_duration_matches = 0
        # first_match = None
        # for m in potential_matches:
        #     if abs(m.duration - m.window_size) < self._duration_delta:
        #         if first_match is None:
        #             first_match = m
        #         if first_match and first_match == m:
        #             n_duration_matches += 1
        #         if n_duration_matches >= self._n_consecutive_matches_threshold:
        #             # can be confident in this case so yield the first match with the largest duration
        #             yield first_match
        #             return

        # handle the case where there are multiple distinct matches that cover the window when aligned by offset
        potential_matches.sort(key=lambda m: int(m.offset)) # sort by offset, so first match in window is first
        offsets_to_matches = defaultdict(list)
        window_size_sum = 0
        n_matches = 0
        for offset, group in itertools.groupby(potential_matches, key=lambda m: int(m.offset)):
            for match in group:
                if len(offsets_to_matches[offset]) == 0:
                    offsets_to_matches[offset].append(match)
                else:
                    if match == offsets_to_matches[offset][0]:
                        offsets_to_matches[offset].append(match)
                window_size_sum += match.window_size
                n_matches += 1
        average_window_size = window_size_sum / n_matches
        percentage_window_covered = 0
        for offset, matches in offsets_to_matches.items():
            if len(matches) >= self._n_consecutive_matches_threshold:
                min_duration_match = min(matches, key=lambda m: m.duration)
                average_duration = sum(map(lambda m: m.duration, matches)) / len(matches)
                percentage_window_covered += (average_duration/average_window_size)
                yield min_duration_match
            if percentage_window_covered > self._percentage_window_covered:
                return





    async def match(self, track: IderTrack) -> int:
        n_segments_saved = 0
        n_segments = 0
        with TemporaryDirectory() as tmp_dir:
            output_path = (Path(tmp_dir) / Path(track.title)).with_suffix(track.file_path.suffix)
            start = 0
            window_size = self._window_size
            matches_found = defaultdict(list)
            while (start + window_size) < track.duration:
                block_saved = False
                window_size = self._window_size
                for _ in range(self._n_rounds):
                    await self._ffmpeg_controller.make_segment(int(start), track.file_path, window_size, output_path)
                    n_segments += 1
                    fingerprint = await self._fpcalc_controller.calculate_fingerprint(output_path)
                    async for match in self._acoustid_client.search_for_match(fingerprint, window_size):
                        if match:
                            segment_start = start + match.offset
                            segment_end = segment_start + match.duration
                            assert segment_start < segment_end, match
                            logger.info("match found, from %f to %f detail: %s", start + match.offset, start + match.duration, match)
                            self._db_controller.upload_track_segment(
                                track.beets_id, segment_start, segment_end, match.mb_id, match.artist, match.title, int(start), window_size, n_segments
                            )
                            n_segments_saved += 1
                            block_saved = True
                    window_size += self._consecutive_matches_offset_s

                if not block_saved:
                    logger.info("no match found in window %d:%d, sliding window along by 1 second.", start, start + window_size)
                    start += 1
                else:
                    start += self._window_size

        logger.info("saved %d segments to db", n_segments_saved)
        logger.info("matches found %s", matches_found)
        return n_segments_saved
