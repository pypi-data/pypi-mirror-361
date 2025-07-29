from __future__ import annotations
import asyncio
from json import JSONDecodeError
import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TypedDict

from raphson_mp import process, settings, track
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import AudioFormat


_LOGGER = logging.getLogger(__name__)
_FFMPEG = "ffmpeg"
_LOUDNORM_I = -15.5  # TODO slowly increase from -16 to -14. 2025H1 -15.5 | 2025H2 -15 | 2026H1 -14.5 | 2026H2 -14
_LOUDNORM_LRA = 20
_LOUDNORM_TP = -1


def common_opts():
    return [
        _FFMPEG,
        "-hide_banner",
        "-nostats",
    ]


async def image_thumbnail(
    image: bytes, img_format: ImageFormat, img_quality: ImageQuality, square: bool
) -> bytes:
    size = img_quality.resolution

    if square:
        thumb_filter = f"scale={size}:{size}:force_original_aspect_ratio=increase,crop={size}:{size}"
    else:
        thumb_filter = f"scale={size}:{size}:force_original_aspect_ratio=decrease"

    if img_format is ImageFormat.WEBP:
        format_options = ["-pix_fmt", "yuv420p", "-f", "webp"]
    elif img_format is ImageFormat.JPEG:
        format_options = ["-pix_fmt", "yuvj420p", "-f", "mjpeg"]

    with NamedTemporaryFile() as temp_input, NamedTemporaryFile() as temp_output:
        await asyncio.to_thread(temp_input.write, image)
        await asyncio.to_thread(temp_input.flush)
        await process.run(
            *common_opts(),
            "-loglevel", settings.ffmpeg_log_level,
            "-y", # overwrite the temp file, it already exists
            "-i",
            temp_input.name,
            "-filter",
            thumb_filter,
            *format_options,
            temp_output.name,
        )
        return await asyncio.to_thread(temp_output.read)


async def check_image(image_data: bytes):
    """Check if the provided image data is valid (not corrupt)"""
    try:
        await image_thumbnail(image_data, ImageFormat.JPEG, ImageQuality.LOW, False)
        return True
    except process.ProcessReturnCodeError:
        return False


class LoudnessParams(TypedDict):
    input_i: float
    input_tp: float
    input_lra: float
    input_thresh: float
    target_offset: float
    normalization_type: str


def _parse_loudness(stderr: bytes) -> LoudnessParams:
    # Manually find the start of loudnorm info json
    try:
        meas_out = stderr.decode(encoding="utf-8")
    except UnicodeDecodeError:
        meas_out = stderr.decode(encoding="latin-1")
    start = meas_out.rindex("Parsed_loudnorm_0") + 37
    end = start + meas_out[start:].index("}") + 1
    json_text = meas_out[start:end]
    try:
        meas_json = json.loads(json_text)
    except JSONDecodeError as ex:
        _LOGGER.error("Invalid json: %s", json_text)
        _LOGGER.error("Original output: %s", meas_out)
        raise ex

    _LOGGER.info("Measured integrated loudness: %s", meas_json["input_i"])

    return {
        "input_i": float(meas_json["input_i"]),
        "input_tp": float(meas_json["input_tp"]),
        "input_lra": float(meas_json["input_lra"]),
        "input_thresh": float(meas_json["input_thresh"]),
        "target_offset": float(meas_json["target_offset"]),
        "normalization_type": meas_json["normalization_type"],
    }


async def measure_loudness(measure_path: Path) -> LoudnessParams:
    # First phase of 2-phase loudness normalization
    # https://k.ylo.ph/2016/04/04/loudnorm.html

    _LOGGER.info("Measuring loudness: %s", measure_path.as_posix())
    # Annoyingly, loudnorm outputs to stderr instead of stdout. Disabling logging also
    # hides the loudnorm output, so we must parse loudnorm from the output.
    _stdout, stderr = await process.run_output(
        *common_opts(),
        "-i",
        measure_path.as_posix(),
        "-map",
        "0:a",
        "-filter:a",
        "loudnorm=print_format=json",
        "-f",
        "null",
        "-",
    )

    return _parse_loudness(stderr)


def _get_loudnorm_filter(measured_loudness: LoudnessParams):
    base_filter = f"loudnorm=I={_LOUDNORM_I}:LRA={_LOUDNORM_LRA}:TP={_LOUDNORM_TP}"

    # if measured_loudness is None :
    #     # If no measured loudness is available, use single pass loudness filter
    #     return base_filter

    if measured_loudness["input_i"] > 0:
        _LOGGER.warning(
            "Integrated loudness is positive. This should be impossible, but can happen "
            + "with input files containing out of range values. Using dynamic single-pass loudnorm filter.")

    return (
        f"{base_filter}:"
        + f"measured_I={measured_loudness['input_i']}:"
        + f"measured_TP={measured_loudness['input_tp']}:"
        + f"measured_LRA={measured_loudness['input_lra']}:"
        + f"measured_thresh={measured_loudness['input_thresh']}:"
        + f"offset={measured_loudness['target_offset']}:"
        + "linear=true:"
        + "print_format=json"
    )


async def transcode_audio(
    input_path: Path,
    input_loudness: LoudnessParams,
    output_format: AudioFormat,
    output_path: Path,
    track: track.Track | None = None,
):
    _LOGGER.info("Transcoding audio: %s", input_path.as_posix())

    if output_format in {AudioFormat.WEBM_OPUS_HIGH, AudioFormat.WEBM_OPUS_LOW}:
        input_options = [
            "-map",
            "0:a",  # only keep audio
            "-map_metadata",
            "-1",  # discard metadata
        ]
        bit_rate = "128k" if output_format == AudioFormat.WEBM_OPUS_HIGH else "48k"
        audio_options = [
            "-f",
            "webm",
            "-c:a",
            "libopus",
            "-b:a",
            bit_rate,
            "-vbr",
            "on",
            # Higher frame duration offers better compression at the cost of latency
            "-frame_duration",
            "60",
            "-vn",
        ]  # remove video track (and album covers)
    elif output_format is AudioFormat.MP3_WITH_METADATA:
        assert track, "track must be provided when transcoding to MP3"

        cover = await track.get_cover(False, ImageQuality.HIGH, img_format=ImageFormat.JPEG)
        # Write cover to temp file so ffmpeg can read it
        # cover_temp_file = tempfile.NamedTemporaryFile('wb')  # pylint: disable=consider-using-with
        cover_temp_file = open("/tmp/test", "wb")
        cover_temp_file.write(cover)

        # https://trac.ffmpeg.org/wiki/Encode/MP3
        input_options = [
            "-i",
            cover_temp_file.name,  # add album cover
            "-map",
            "0:a",  # include audio stream from first input
            "-map",
            "1:0",  # include first stream from second input
            "-id3v2_version",
            "3",
            "-map_metadata",
            "-1",  # discard original metadata
            "-metadata:s:v",
            "title=Album cover",
            "-metadata:s:v",
            "comment=Cover (front)",
            *track.get_ffmpeg_options(),
        ]  # set new metadata

        audio_options = [
            "-f",
            "mp3",
            "-c:a",
            "libmp3lame",
            "-c:v",
            "copy",  # Leave cover as JPEG, don't re-encode as PNG
            "-q:a",
            "2",
        ]  # VBR 190kbps
    else:
        raise ValueError(output_format)

    _stdout, stderr = await process.run_output(
        *common_opts(),
        "-y",  # overwriting file is required, because the created temp file already exists
        "-i",
        input_path.as_posix(),
        *input_options,
        *audio_options,
        "-t",
        str(settings.track_max_duration_seconds),
        "-ac",
        "2",
        "-filter:a",
        _get_loudnorm_filter(input_loudness),
        output_path.as_posix(),
    )

    loudness2 =_parse_loudness(stderr)

    if loudness2["normalization_type"] != "linear":
        _LOGGER.warning('dynamic normalization was used for: %s', input_path.as_posix())

    if output_format is AudioFormat.MP3_WITH_METADATA:
        cover_temp_file.close()  # pyright: ignore[reportPossiblyUnboundVariable]
