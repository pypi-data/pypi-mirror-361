import asyncio
import logging
import time
from dataclasses import dataclass
from sqlite3 import Connection
from typing import cast

from raphson_mp import db, event, lastfm
from raphson_mp.auth import PrivacyOption, StandardUser, User
from raphson_mp.common.control import ClientPlaying, ServerPlaying
from raphson_mp.track import Track

_LOGGER = logging.getLogger(__name__)


@dataclass
class NowPlaying:
    player_id: str
    user_id: int
    username: str
    update_time: int
    lastfm_update_timestamp: int
    expiry: int
    data: ClientPlaying

    def control_command(self, conn: Connection) -> ServerPlaying:
        track = Track.maybe(conn, self.data.track)
        return ServerPlaying(
            player_id=self.player_id,
            username=self.username,
            update_time=self.update_time,
            paused=self.data.paused,
            position=self.data.position,
            duration=self.data.duration,
            control=self.data.control,
            volume=self.data.volume,
            expiry=self.expiry,
            client=self.data.client,
            track=track.to_dict() if track else None,
            virtual_track=self.data.virtual_track,
            queue=self.data.queue,
            playlists=self.data.playlists,
        )


_NOW_PLAYING: dict[str, NowPlaying] = {}


def now_playing() -> list[NowPlaying]:
    current_time = int(time.time())
    return [entry for entry in _NOW_PLAYING.values() if entry.update_time > current_time - entry.expiry]


async def set_now_playing(
    conn: Connection,
    user: User,
    player_id: str,
    expiry: int,
    data: ClientPlaying,
) -> None:
    current_time = int(time.time())
    username = user.nickname if user.nickname else user.username

    now_playing = _NOW_PLAYING[player_id] = NowPlaying(
        player_id,
        user.user_id,
        username,
        current_time,
        current_time,
        expiry,
        data,
    )

    if not data.paused and now_playing.lastfm_update_timestamp < current_time - 60:
        user_key = lastfm.get_user_key(cast(StandardUser, user))
        if user_key:
            track = Track.maybe(conn, data.track)
            if track:
                await lastfm.update_now_playing(user_key, track)
                now_playing.lastfm_update_timestamp = current_time

    await event.fire(event.NowPlayingEvent(now_playing))


async def set_played(user: User, track: Track, timestamp: int):
    private = user.privacy == PrivacyOption.AGGREGATE

    if not private:
        await event.fire(event.TrackPlayedEvent(user, timestamp, track))

    def thread():
        with db.connect() as writable_conn:
            writable_conn.execute(
                """
                INSERT INTO history (timestamp, user, track, playlist, private)
                VALUES (?, ?, ?, ?, ?)
                """,
                (timestamp, user.user_id, track.path, track.playlist, private),
            )

    await asyncio.to_thread(thread)

    # last.fm requires track length to be at least 30 seconds
    if not private and track.duration >= 30:
        lastfm_key = lastfm.get_user_key(cast(StandardUser, user))
        if lastfm_key:
            await lastfm.scrobble(lastfm_key, track, timestamp)


async def stop_playing(user: User, player_id: str):
    playing = _NOW_PLAYING.get(player_id)
    if playing is None:
        return

    if playing.user_id != user.user_id:
        _LOGGER.warning("user %s attempted to stop player owned by different user %s", user.username, playing.user_id)
        return

    _LOGGER.debug("player %s stopped playing", player_id)
    del _NOW_PLAYING[player_id]
    await event.fire(event.StoppedPlayingEvent(player_id))
