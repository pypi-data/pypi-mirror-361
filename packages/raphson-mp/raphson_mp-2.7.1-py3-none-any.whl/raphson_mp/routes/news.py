import asyncio
from pathlib import Path
import tempfile
from sqlite3 import Connection

from aiohttp import web

from raphson_mp import ffmpeg, httpclient, settings
from raphson_mp.auth import User
from raphson_mp.common.track import AudioFormat
from raphson_mp.decorators import route


@route("/audio")
async def audio(_request: web.Request, _conn: Connection, _user: User):
    with tempfile.NamedTemporaryFile() as temp_input, tempfile.NamedTemporaryFile() as temp_output:
        if not settings.news_server:
            raise web.HTTPServiceUnavailable(reason="news server not configured")

        # Download wave audio to temp file
        async with httpclient.session(settings.news_server) as session:
            async with session.get("/news.wav", raise_for_status=False) as response:
                if response.status == 503:
                    raise web.HTTPServiceUnavailable(reason="news not available")

                response.raise_for_status()

                name = response.headers["X-Name"]

                while chunk := await response.content.read(1024 * 1024):
                    await asyncio.to_thread(temp_input.write, chunk)

        temp_input.flush()

        input_path = Path(temp_input.name)
        output_path = Path(temp_output.name)

        loudness = await ffmpeg.measure_loudness(input_path)
        await ffmpeg.transcode_audio(input_path, loudness, AudioFormat.WEBM_OPUS_LOW, output_path)

        audio_bytes = await asyncio.to_thread(temp_output.read)

    return web.Response(body=audio_bytes, content_type="audio/webm", headers={"X-Name": name})
