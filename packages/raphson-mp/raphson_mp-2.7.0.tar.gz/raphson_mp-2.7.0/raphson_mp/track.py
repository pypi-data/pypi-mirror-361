from __future__ import annotations

import json
import logging
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path
from sqlite3 import Connection

from aiohttp import web

from raphson_mp import (
    cache,
    ffmpeg,
    process,
    settings,
)
from raphson_mp.common import metadata
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.lyrics import Lyrics
from raphson_mp.common.lyrics import from_text as lyrics_from_text
from raphson_mp.common.track import MUSIC_EXTENSIONS, AudioFormat, NoSuchTrackError, TrackBase, is_trashed

log = logging.getLogger(__name__)


def to_relpath(path: Path) -> str:
    """
    Returns: Relative path as string, excluding base music directory
    """
    relpath = path.as_posix()[len(settings.music_dir.as_posix()) + 1 :]
    return relpath if len(relpath) > 0 else ""


def from_relpath(relpath: str) -> Path:
    """
    Creates Path object from string path relative to music base directory, with directory
    traversal protection.
    """
    if relpath and (relpath[0] == "/" or relpath[-1] == "/"):
        raise ValueError("relpath must not start or end with slash: " + relpath)

    # resolve() is important for is_relative_to to work properly!
    path = Path(settings.music_dir, relpath).resolve()

    if not path.is_relative_to(settings.music_dir):
        raise ValueError(f"path {path.as_posix()} is not inside music base directory {settings.music_dir.as_posix()}")

    return path


def list_tracks_recursively(path: Path, trashed: bool = False) -> Iterator[Path]:
    """
    Scan directory for tracks, recursively
    Args:
        path: Directory Path
    Returns: Paths iterator
    """
    for ext in MUSIC_EXTENSIONS:
        for track_path in path.glob("**/*." + ext):
            if is_trashed(track_path) == trashed:
                yield track_path


class Track(TrackBase):
    def __init__(self, conn: Connection, relpath: str):
        query = "SELECT mtime, ctime, duration, title, album, album_artist, track_number, year, video, lyrics FROM track WHERE path=?"
        row = conn.execute(query, (relpath,)).fetchone()
        if row is None:
            raise NoSuchTrackError("Missing track from database: " + relpath)

        mtime, ctime, duration, title, album, album_artist, track_number, year, video, lyrics = row

        rows = conn.execute("SELECT artist FROM track_artist WHERE track=?", (relpath,)).fetchall()
        artists = metadata.sort_artists([row[0] for row in rows], album_artist)

        rows = conn.execute("SELECT tag FROM track_tag WHERE track=?", (relpath,)).fetchall()
        tags = [row[0] for row in rows]

        super().__init__(
            path=relpath,
            mtime=mtime,
            ctime=ctime,
            duration=duration,
            title=title,
            album=album,
            album_artist=album_artist,
            year=year,
            track_number=track_number,
            video=video,
            lyrics=lyrics,
            artists=artists,
            tags=tags,
        )

    @property
    def filepath(self) -> Path:
        return from_relpath(self.path)

    async def get_loudness(self) -> ffmpeg.LoudnessParams:
        async def data_func():
            loudness = await ffmpeg.measure_loudness(self.filepath)
            # Cache for a year: expensive to calculate, result doesn't really change and orphan entries take up very little space
            return cache.CacheData(json.dumps(loudness).encode(), cache.YEAR)

        data = await cache.retrieve_or_store(f"loud4{self.path}{self.mtime}", data_func)
        return json.loads(data)

    async def transcoded_audio(self, audio_format: AudioFormat) -> web.StreamResponse:
        """
        Normalize and compress audio using ffmpeg
        Returns: Compressed audio bytes
        """

        async def data_func(output_path: Path):
            loudness = await self.get_loudness()
            await ffmpeg.transcode_audio(self.filepath, loudness, audio_format, output_path, self)
            # Audio for sure doesn't change so ideally we'd cache for longer, but that would mean
            # deleted tracks remain in the cache for longer as well.
            return cache.YEAR

        return await cache.retrieve_or_store_response(
            f"audio{audio_format.value}{self.path}", audio_format.content_type, data_func
        )

    async def get_cover(self, meme: bool, img_quality: ImageQuality, img_format: ImageFormat) -> bytes:
        """
        Find album cover using MusicBrainz or Bing.
        Parameters:
            meta: Track metadata
        Returns: Album cover image bytes, or None if MusicBrainz nor bing found an image.
        """
        from raphson_mp import album

        if self.album and not metadata.album_is_compilation(self.album):
            search_album = self.album
        elif self.title:
            search_album = self.title
        else:
            search_album = self.display_title(show_album=False, show_year=False)

        search_artist = self.album_artist if self.album_artist else self.primary_artist

        return await album.get_cover_thumbnail(search_artist, search_album, meme, img_quality, img_format)

    async def get_lyrics(self) -> Lyrics | None:
        if self.lyrics:
            log.info("using lyrics from metadata")
            return lyrics_from_text("metadata", self.lyrics)

        from raphson_mp import lyrics

        artist = self.primary_artist
        if self.title and artist:
            return await lyrics.find(self.title, artist, self.album, self.duration)

        log.info("can't search for lyrics due to missing metadata")
        return None

    def get_ffmpeg_options(self, option: str = "-metadata") -> list[str]:
        def convert(value: str | int | list[str] | None):
            if value is None:
                return ""
            if type(value) == list:
                return metadata.join_meta_list(value)
            return str(value)

        metadata_options: list[str] = [
            option,
            "album=" + convert(self.album),
            option,
            "artist=" + convert(self.artists),
            option,
            "title=" + convert(self.title),
            option,
            "date=" + convert(self.year),
            option,
            "album_artist=" + convert(self.album_artist),
            option,
            "track=" + convert(self.track_number),
            option,
            "lyrics=" + convert(self.lyrics),
            option,
            "genre=" + convert(self.tags),
        ]
        # Remove alternate lyrics tags
        for tag in metadata.ALTERNATE_LYRICS_TAGS:
            metadata_options.extend((option, tag + "="))
        return metadata_options

    async def save(self):
        """
        Write metadata to file
        """
        original_extension = self.path[self.path.rindex(".") - 1 :]
        # ogg format seems to require setting metadata in stream instead of container
        metadata_flag = "-metadata:s" if original_extension == ".ogg" else "-metadata"
        with tempfile.NamedTemporaryFile(suffix=original_extension) as temp_file:
            await process.run(
                *ffmpeg.common_opts(),
                "-y",  # overwriting file is required, because the created temp file already exists
                "-i",
                self.filepath.as_posix(),
                "-codec",
                "copy",
                *self.get_ffmpeg_options(metadata_flag),
                temp_file.name,
            )
            shutil.copy(temp_file.name, self.filepath)

    @classmethod
    def maybe(cls, conn: Connection, relpath: str | None) -> Track | None:
        try:
            return Track(conn, relpath) if relpath is not None else None
        except NoSuchTrackError:
            return None


def filter_tracks(
    conn: Connection,
    limit: int,
    offset: int,
    *,
    playlist: str | None = None,
    artist: str | None = None,
    tag: str | None = None,
    album_artist: str | None = None,
    album: str | None = None,
    year: int | None = None,
    title: str | None = None,
    has_metadata: bool | None = None,
    order: str | None = None,
) -> list[Track]:
    select_query = "SELECT path FROM track"
    where_query = "WHERE true"
    params: list[str | int] = []
    if playlist:
        where_query += " AND playlist = ?"
        params.append(playlist)

    if artist:
        select_query += " JOIN track_artist ON path = track"
        where_query += " AND artist = ?"
        params.append(artist)

    if tag:
        select_query += " JOIN track_tag ON path = track"
        where_query += " AND tag = ?"
        params.append(tag)

    if album_artist:
        where_query += " AND album_artist = ?"
        params.append(album_artist)

    if album:
        where_query += " AND album = ?"
        params.append(album)

    if year:
        where_query += " AND year = ?"
        params.append(year)

    if title:
        where_query += " AND title = ?"
        params.append(title)

    if has_metadata:
        # Has at least metadata for: title, album, album artist, artists
        where_query += """
            AND title NOT NULL
            AND album NOT NULL
            AND album_artist NOT NULL
            AND EXISTS(SELECT artist FROM track_artist WHERE track = path)
            """

    if has_metadata is False:
        where_query += """ AND (
            title IS NULL
            OR album IS NULL
            OR album_artist IS NULL
            OR NOT EXISTS(SELECT artist FROM track_artist WHERE track = path)
            OR year IS NULL
            )"""

    if order:
        order_query_parts: list[str] = []
        for order_item in order.split(","):
            if order_item == "title":
                order_query_parts.append("title ASC")
            elif order_item == "ctime_asc":
                order_query_parts.append("ctime ASC")
            elif order_item == "ctime_desc":
                order_query_parts.append("ctime DESC")
            elif order_item == "year_desc":
                where_query += " AND YEAR IS NOT NULL"
                order_query_parts.append("year DESC")
            elif order_item == "random":
                order_query_parts.append("RANDOM()")
            elif order_item == "number":
                order_query_parts.append("track_number ASC")
            else:
                log.warning("ignoring invalid order: %s", order)
        order_query = "ORDER BY " + ", ".join(order_query_parts)
    else:
        order_query = ""

    query = f"{select_query} {where_query} {order_query} LIMIT {limit} OFFSET {offset}"

    log.debug("filter: %s", query)

    result = conn.execute(query, params)
    return [Track(conn, relpath) for relpath, in result]
