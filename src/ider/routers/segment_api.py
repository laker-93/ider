from typing import Optional

from fastapi import APIRouter, Depends, Request

from ider.clients.acoustid_client import AcoustIDClient
from ider.clients.beets_client import BeetsClient
from ider.controllers.db_controller import DbController
from ider.controllers.fpcalc_controller import FPCalcController

router = APIRouter()


async def get_db_controller(req: Request) -> DbController:
    return req.app.state.db_controller


async def get_beets_client(req: Request) -> BeetsClient:
    return req.app.state.beets_client

async def get_fp_calc_controller(req: Request) -> FPCalcController:
    return req.app.state.fp_calc_controller

async def get_acoustid_client(req: Request) -> AcoustIDClient:
    return req.app.state.acoustid_client


@router.post("/push_fingerprints")
async def push_fingerprints(
        user: str, beets_client: BeetsClient = Depends(get_beets_client),
        fp_calc_controller: FPCalcController = Depends(get_fp_calc_controller),
        acoustid_client: AcoustIDClient = Depends(get_acoustid_client)
) -> bool:
    ider_tracks = await beets_client.get_paths_of_users_tracks(user)
    await fp_calc_controller.calculate_fpcalc(ider_tracks)
    await acoustid_client.push_fingerprints(ider_tracks)
    return True


@router.post("/create_segment")
async def create_segment(
        beets_client: BeetsClient = Depends(get_beets_client)
) -> bool:
    track_path = await beets_client.get_path_of_track(1)
    print(track_path)
    return True


@router.get("/get_segment")
def get_segment(
        track_id: int, time: int, db_controller: DbController = Depends(get_db_controller)
) -> Optional[str]:
    mbid = db_controller.get_mbid_by_time(track_id, time)
    return mbid
