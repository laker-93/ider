from pathlib import Path
from tinydb import TinyDB

from ider.controllers.db_controller import DbController


def create_db_session(db_path: Path) -> TinyDB:
    if not db_path.exists():
        db_path.parent.mkdir(parents=True)
    return TinyDB(db_path)


def create_db_controller(app_env: str) -> DbController:
    return DbController(
        db=create_db_session(
            Path('../db/db.json')
        ),
        app_env=app_env,
    )
