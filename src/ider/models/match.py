from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Match:
    mb_id: str
    artist: str
    title: str
    duration: float
    window_size: float
    offset: int

    def __eq__(self, other: Self):
        return self.mb_id == other.mb_id and self.artist == other.artist and self.title == other.title

    def __hash__(self):
        return hash((self.mb_id, self.artist, self.title))
