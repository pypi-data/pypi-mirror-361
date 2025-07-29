from dataclasses import dataclass


@dataclass
class Album:
    name: str
    artist: str | None
    track: str # arbitrary track from the album, can be used to obtain a cover art image


@dataclass
class Artist:
    name: str
