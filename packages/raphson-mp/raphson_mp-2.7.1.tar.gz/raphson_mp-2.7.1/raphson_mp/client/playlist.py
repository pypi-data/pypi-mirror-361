from dataclasses import dataclass


@dataclass(kw_only=True)
class Playlist:
    name: str
    track_count: int
    favorite: bool
    write: bool
