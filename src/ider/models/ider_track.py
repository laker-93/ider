from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class IderTrack:
    file_path: Path
    beets_id: int
    title: str
    artist: str
    musicbrainz_id: str
    fingerprint: Optional[str] = None

