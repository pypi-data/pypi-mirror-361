import asyncio
import dataclasses
import logging
from pathlib import Path
from sqlite3 import Connection
from tempfile import NamedTemporaryFile
from typing import Any

from aiohttp import web

from raphson_mp import (
    acoustid,
    cache,
    ffmpeg,
    musicbrainz,
    process,
    scanner,
    db,
)
from raphson_mp.common import lyrics
from raphson_mp.auth import User
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.lyrics import PlainLyrics, TimeSyncedLyrics
from raphson_mp.common.track import AudioFormat, NoSuchTrackError, relpath_playlist
from raphson_mp.decorators import route
from raphson_mp.track import Track
from raphson_mp.playlist import Playlist

log = logging.getLogger(__name__)


def _track(conn: Connection, relpath: str) -> Track:
    try:
        track = Track(conn, relpath)
    except NoSuchTrackError:
        raise web.HTTPNotFound(reason="track not found")
    return track


@route("/{relpath}/info")
async def route_info(request: web.Request, conn: Connection, _user: User):
    relpath = request.match_info["relpath"]
    track = _track(conn, relpath)
    return web.json_response(track.to_dict())


@route("/{relpath}/video")
async def route_video(request: web.Request, conn: Connection, _user: User):
    """
    Return video stream
    """
    relpath = request.match_info["relpath"]
    track = _track(conn, relpath)

    if track.video == "vp9":
        output_format = "webm"
        output_media_type = "video/webm"
    elif track.video == "h264":
        output_format = "mp4"
        output_media_type = "video/mp4"
    else:
        raise web.HTTPBadRequest(reason="file has no suitable video stream")

    cache_key: str = f"video{track.path}{track.mtime}"

    response = await cache.retrieve_response(cache_key, output_media_type)

    if response is None:
        with NamedTemporaryFile() as tempfile:
            await process.run(
                *ffmpeg.common_opts(),
                "-y",
                "-i",
                track.filepath.as_posix(),
                "-c:v",
                "copy",
                "-map",
                "0:v",
                "-f",
                output_format,
                tempfile.name,
            )
            await cache.store(cache_key, Path(tempfile.name), cache.MONTH)
        response = await cache.retrieve_response(cache_key, output_media_type)
        if response is None:
            raise ValueError()

    return response


@route("/{relpath}/audio")
async def route_audio(request: web.Request, conn: Connection, _user: User):
    """
    Get transcoded audio for the given track path.
    """
    relpath = request.match_info["relpath"]
    track = _track(conn, relpath)

    audio_format = AudioFormat(request.query["type"])

    response = await track.transcoded_audio(audio_format)
    if audio_format is AudioFormat.MP3_WITH_METADATA:
        mp3_name = track.download_name()
        response.headers["Content-Disposition"] = f'attachment; filename="{mp3_name}"'

    if 'mtime' in request.query: # if cache busting mtime is present, we can serve with a long cache time
        response.headers['Cache-Control'] = 'immutable, max-age=604800'
    return response


@route("/{relpath}/cover")
async def route_album_cover(request: web.Request, conn: Connection, _user: User):
    """
    Get album cover image for the provided track path.
    """
    relpath = request.match_info["relpath"]
    track = _track(conn, relpath)

    quality = ImageQuality(request.query.get("quality", ImageQuality.HIGH))
    format = ImageFormat(request.query.get("format", ImageFormat.WEBP))
    meme = bool(int(request.query.get("meme", "0")))

    image_bytes = await track.get_cover(meme, quality, format)

    response = web.Response(body=image_bytes, content_type=format.content_type)
    if 'mtime' in request.query: # if cache busting mtime is present, we can serve with a long cache time
        response.headers['Cache-Control'] = 'immutable, max-age=604800'
    return response


@route("/{relpath}/lyrics")
async def route_lyrics(request: web.Request, conn: Connection, _user: User):
    """
    Get lyrics for the provided track path.
    """
    relpath = request.match_info["relpath"]
    track = _track(conn, relpath)

    lyr = await track.get_lyrics()

    if "type" in request.query:
        if request.query["type"] == "plain" and isinstance(lyr, TimeSyncedLyrics):
            lyr = lyr.to_plain()
        elif request.query["type"] == "synced" and isinstance(lyr, PlainLyrics):
            lyr = None

    response = web.json_response(lyrics.to_dict(lyr))
    if 'mtime' in request.query: # if cache busting mtime is present, we can serve with a long cache time
        response.headers['Cache-Control'] = 'immutable, max-age=604800'
    return response


@route("/{relpath}/update_metadata", method="POST")
async def route_update_metadata(request: web.Request, conn: Connection, user: User):
    """
    Endpoint to update track metadata
    """
    relpath = request.match_info["relpath"]
    track = _track(conn, relpath)

    playlist = Playlist(conn, relpath_playlist(relpath), user)
    if not playlist.is_writable():
        raise web.HTTPForbidden(reason="No write permission for this playlist")

    json = await request.json()
    track.title = json["title"]
    track.album = json["album"]
    track.artists = json["artists"]
    track.album_artist = json["album_artist"]
    track.tags = json["tags"]
    track.year = json["year"]
    track.track_number = json["track_number"]
    track.lyrics = json["lyrics"]

    await track.save()

    await scanner.scan_track(user, track.filepath)

    raise web.HTTPNoContent()


@route("/{relpath}/acoustid")
async def route_acoustid(request: web.Request, conn: Connection, _user: User):
    relpath = request.match_info["relpath"]
    track = _track(conn, relpath)
    fp = await acoustid.get_fingerprint(track.filepath)

    async for result in acoustid.lookup(fp):
        log.info("found track=%s recording=%s", result.acoustid_track_id, result.mb_recording_id)

        meta_list: list[dict[str, Any]] = []
        known_ids: set[str] = set()
        async for meta in musicbrainz.get_recording_metadata(result.mb_recording_id):
            if meta.id in known_ids:
                continue
            log.info("found possible metadata: %s", meta)
            meta_list.append(dataclasses.asdict(meta))
            known_ids.add(meta.id)

        return web.json_response({
            "acoustid": result.acoustid_track_id,
            "releases": meta_list,
        })

    raise web.HTTPNoContent()


@route("/{relpath}/report_problem", method="POST")
async def report_problem(request: web.Request, conn: Connection, _user: User):
    relpath = request.match_info["relpath"]

    _ = _track(conn, relpath) # just to verify the track exists

    def thread():
        with db.connect() as writable_conn:
            writable_conn.execute("INSERT OR IGNORE INTO track_problem VALUES (?)", (relpath,))

    await asyncio.to_thread(thread)

    raise web.HTTPNoContent()
