import logging
from typing import Optional

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
    ider_tracks = await beets_client.get_paths_of_users_tracks(user)
    logger.info("found %d tracks for user %s", len(ider_tracks), user)
    await fp_calc_controller.set_fingerprints(ider_tracks)
    await acoustid_client.push_fingerprints(ider_tracks)
    return len(ider_tracks)

@router.post("/match_segments")
async def match_segments(
        user: str, beet_id: int, beets_client: BeetsClient = Depends(get_beets_client),
        match_orchestrator: MatchOrchestrator = Depends(get_match_orchestrator),
) -> int:
    ider_track = await beets_client.get_path_of_public_user_track(beet_id, user)
    await match_orchestrator.match(ider_track)



@router.get("/get_segment")
def get_segment(
        track_id: int, time: int, db_controller: DbController = Depends(get_db_controller)
) -> Optional[str]:
    mbid = db_controller.get_mbid_by_time(track_id, time)
    return mbid
