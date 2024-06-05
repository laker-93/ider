from contextlib import asynccontextmanager
from typing import Dict

import yaml
from pathlib import Path

from aiohttp import BasicAuth
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ider.clients.acoustid_client import AcoustIDClient
from ider.clients.beets_client import BeetsClient
from ider.controllers.db_controller import DbController
from ider.controllers.ffmpeg_controller import FFMPEGController
from ider.controllers.fpcalc_controller import FPCalcController
from ider.factories.create_aiohttp_session import init_aiohttp_session
from ider.factories.create_db import create_db_controller
from ider.orchestrators.match_orchestrator import MatchOrchestrator
from ider.routers import segment_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_controller = create_db_controller(app.state.app_env)
    app.state.db_controller = db_controller
    app.state.fp_calc_controller = FPCalcController()
    async with init_aiohttp_session(
    ) as beets_session, init_aiohttp_session(
        auth=BasicAuth('acoustid', 'acoustid')
    ) as acoustid_session:
        app.state.beets_client = BeetsClient(
            app.state.beets_user_client_addr,
            app.state.beets_public_client_addr,
            beets_session
        )
        acoustid_client = AcoustIDClient(
            app.state.acoustid_client_addr,
            acoustid_session
        )
        app.state.acoustid_client = acoustid_client
        app.state.match_orchestrator = MatchOrchestrator(
            ffmpeg_controller=FFMPEGController(),
            fpcalc_controller=FPCalcController(),
            acoustid_client=acoustid_client,
            db_controller=db_controller,
            config=app.state.matching_algo_config
        )
        yield


def create_app(app_config: Dict):
    app_env = app_config["app_env"]
    beets_user_client_addr = app_config["beets_user_client_addr"]
    beets_public_client_addr = app_config["beets_public_client_addr"]
    acoustid_client_addr = app_config["acoustid_client_addr"]
    matching_algo_config = app_config['matching_algorithm']
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.app_env = app_env
    app.state.beets_user_client_addr = beets_user_client_addr
    app.state.beets_public_client_addr = beets_public_client_addr
    app.state.acoustid_client_addr = acoustid_client_addr
    app.state.matching_algo_config = matching_algo_config

    app.include_router(segment_api.router)
    return app


def get_config(environment: str) -> dict:
    config_file_base = Path(__file__).parent.parent / "config" / "config.base.yaml"
    conf_base = yaml.safe_load(config_file_base.read_text())
    config_file = Path(__file__).parent.parent / "config" / f"config.{environment}.yaml"
    app_config = yaml.safe_load(config_file.read_text())
    app_config.update(conf_base)
    return app_config
