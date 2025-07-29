import asyncio
import itertools
import math
from pathlib import Path
import tempfile

from raphson_mp import db, ffmpeg
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import AudioFormat
from raphson_mp.track import Track, from_relpath


async def test_thumbnail():
    image = Path("docs/tyrone_music.jpg").read_bytes()
    options = itertools.product(ImageFormat, ImageQuality, [True, False])
    thumbnails = await asyncio.gather(
        *[ffmpeg.image_thumbnail(image, img_format, img_quality, square) for img_format, img_quality, square in options]
    )
    results = await asyncio.gather(*[ffmpeg.check_image(thumbnail) for thumbnail in thumbnails])
    assert all(results)


async def test_transcode_opus_loudness(track: str):
    input_path = from_relpath(track)

    loudness = await ffmpeg.measure_loudness(input_path)
    assert loudness is not None

    with tempfile.NamedTemporaryFile() as output_tempfile:
        output_path = Path(output_tempfile.name)
        await ffmpeg.transcode_audio(input_path, loudness, AudioFormat.WEBM_OPUS_HIGH, output_path)
        await ffmpeg.transcode_audio(input_path, loudness, AudioFormat.WEBM_OPUS_LOW, output_path)

        # measure output loudness, should be close to loudness target
        loudness2 = await ffmpeg.measure_loudness(output_path)
        assert loudness2 is not None
        assert math.isclose(loudness2["input_i"], ffmpeg._LOUDNORM_I, abs_tol=0.3), loudness2


async def test_transcode_mp3(track: str):
    with db.connect(read_only=True) as conn:
        track_obj = Track(conn, track)

    input_path = from_relpath(track)
    with tempfile.NamedTemporaryFile() as output_tempfile:
        output_path = Path(output_tempfile.name)

        loudness = await ffmpeg.measure_loudness(input_path)
        await ffmpeg.transcode_audio(input_path, loudness, AudioFormat.MP3_WITH_METADATA, output_path, track_obj)
