import hmac
import logging
import time
from sqlite3 import Connection
from weakref import WeakSet, WeakValueDictionary

from aiohttp import WSMsgType, web

from raphson_mp import activity, db, event
from raphson_mp.auth import User
from raphson_mp.common.control import (
    ClientPlaying,
    ClientRelayCommand,
    ClientSubscribe,
    ClientToken,
    ServerFileChange,
    ServerPlayed,
    ServerPlayingStopped,
    Topic,
    parse,
    send,
)
from raphson_mp.decorators import route
from raphson_mp.vars import CLOSE_RESPONSES

_LOGGER = logging.getLogger(__name__)

_BY_ID: WeakValueDictionary[str, web.WebSocketResponse] = WeakValueDictionary()
_SUB_ACTIVITY: WeakSet[web.WebSocketResponse] = WeakSet()

received_message_counter: int = 0


@route("", method="GET")
async def websocket(request: web.Request, conn: Connection, user: User):
    player_id = request.query.get("id")

    if player_id is None:
        raise web.HTTPBadRequest(reason="missing id")

    # If cookies are set, they may have been used to log in and CSRF is possible. In this case,
    # the client must first provide CSRF token before it is trusted.
    trusted = "Cookie" not in request.headers

    ws = web.WebSocketResponse()

    _BY_ID[player_id] = ws
    request.config_dict[CLOSE_RESPONSES].add(ws)

    await ws.prepare(request)

    async for message in ws:
        if message.type == WSMsgType.TEXT:
            try:
                command = parse(message.data)
                _LOGGER.debug("received message %s", command)
            except Exception:
                _LOGGER.warning("failed to parse message %s", message.data)
                continue

            global received_message_counter
            received_message_counter += 1

            if not trusted:
                if isinstance(command, ClientToken):
                    if hmac.compare_digest(user.csrf, command.csrf):
                        trusted = True
                    else:
                        _LOGGER.warning("invalid CSRF token")
                else:
                    _LOGGER.info("ignoring command, client needs to send CSRF token first")
                continue

            if isinstance(command, ClientPlaying):
                await activity.set_now_playing(
                    conn,
                    user,
                    player_id,
                    40,
                    command,
                )
            elif isinstance(command, ClientSubscribe):
                if command.topic == Topic.ACTIVITY:
                    _SUB_ACTIVITY.add(ws)

                    # send current data to the client immediately
                    await send(ws, [playing.control_command(conn) for playing in activity.now_playing()])
            elif isinstance(command, ClientRelayCommand):
                target = _BY_ID.get(command.player_id)
                if target is not None:
                    await send(target, command.server_command())
                else:
                    _LOGGER.warning("unknown player id")
            else:
                _LOGGER.warning("ignoring unsupported command: %s", command)

    return ws


async def broadcast_playing(event: event.NowPlayingEvent) -> None:
    with db.connect(read_only=True) as conn:
        await send(_SUB_ACTIVITY, event.now_playing.control_command(conn))


async def broadcast_stop_playing(event: event.StoppedPlayingEvent) -> None:
    await send(_SUB_ACTIVITY, ServerPlayingStopped(player_id=event.player_id))


async def broadcast_history(event: event.TrackPlayedEvent):
    await send(
        _SUB_ACTIVITY,
        ServerPlayed(
            username=event.user.nickname if event.user.nickname else event.user.username,
            played_time=event.timestamp,
            track=event.track.to_dict(),
        ),
    )


async def broadcast_file_change(event: event.FileChangeEvent):
    username = None
    if event.user:
        username = event.user.nickname if event.user.nickname else event.user.username
    await send(
        _SUB_ACTIVITY,
        ServerFileChange(change_time=int(time.time()), action=event.action, track=event.track, username=username),
    )


event.subscribe(event.NowPlayingEvent, broadcast_playing)
event.subscribe(event.StoppedPlayingEvent, broadcast_stop_playing)
event.subscribe(event.TrackPlayedEvent, broadcast_history)
event.subscribe(event.FileChangeEvent, broadcast_file_change)
