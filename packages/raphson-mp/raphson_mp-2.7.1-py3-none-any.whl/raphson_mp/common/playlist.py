from dataclasses import dataclass
import warnings


@dataclass
class Playlist:
    name: str
    track_count: int
    favorite: bool
    write: bool

    def __init__(self, name: str, track_count: int, favorite: bool, write: bool):
        self.name = name
        self.track_count = track_count
        self.favorite = favorite
        self.write = write

        warnings.warn("Playlist class has been moved to client", DeprecationWarning)
