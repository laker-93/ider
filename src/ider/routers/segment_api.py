import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Tuple, List, Dict

from fastapi import APIRouter, Depends, Request

from ider.clients.acoustid_client import AcoustIDClient
from ider.clients.beets_client import BeetsClient
from ider.controllers.db_controller import DbController
from ider.controllers.fpcalc_controller import FPCalcController
from ider.orchestrators.match_orchestrator import MatchOrchestrator

router = APIRouter()


logger = logging.getLogger(__name__)

async def get_db_controller(req: Request) -> DbController:
    return req.app.state.db_controller

async def get_beets_client(req: Request) -> BeetsClient:
    return req.app.state.beets_client

async def get_fp_calc_controller(req: Request) -> FPCalcController:
    return req.app.state.fp_calc_controller

async def get_acoustid_client(req: Request) -> AcoustIDClient:
    return req.app.state.acoustid_client

async def get_match_orchestrator(req: Request) -> MatchOrchestrator:
    return req.app.state.match_orchestrator

@router.post("/push_fingerprints")
async def push_fingerprints(
        user: str, beets_client: BeetsClient = Depends(get_beets_client),
        fp_calc_controller: FPCalcController = Depends(get_fp_calc_controller),
        acoustid_client: AcoustIDClient = Depends(get_acoustid_client)
) -> int:
    n_tracks = 0
    with TemporaryDirectory() as tmp_dir:
        async for ider_track in beets_client.download_users_tracks(Path(tmp_dir), user):
            ider_track.fingerprint = await fp_calc_controller.calculate_fingerprint(ider_track.file_path)
            fingerprint_pushed = await acoustid_client.push_fingerprints(ider_track)
            if fingerprint_pushed:
                n_tracks += 1
    return n_tracks

@router.post("/match_segments")
async def match_segments(
        user: str, beet_id: int, beets_client: BeetsClient = Depends(get_beets_client),
        match_orchestrator: MatchOrchestrator = Depends(get_match_orchestrator),
) -> int:
    ider_track = await beets_client.get_path_of_public_user_track(beet_id, user)
    segments_matched = await match_orchestrator.match(ider_track)
    return segments_matched



@router.get("/get_segment")
def get_segment(
        track_id: int, time: int, db_controller: DbController = Depends(get_db_controller)
) ->  Optional[Dict[Tuple[Optional[str], str, str], int]]:
    matches = db_controller.get_ids_by_time(track_id, time)
    return matches
