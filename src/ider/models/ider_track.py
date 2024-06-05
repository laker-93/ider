from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class IderTrack:
    file_path: Path
    beets_id: int
    title: str
    artist: str
    duration: Optional[float]
    musicbrainz_id: Optional[str]
    fingerprint: Optional[str] = None

