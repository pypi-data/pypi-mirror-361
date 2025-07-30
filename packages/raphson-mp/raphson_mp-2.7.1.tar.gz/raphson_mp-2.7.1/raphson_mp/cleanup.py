import logging
import time

from raphson_mp import auth, track, settings

log = logging.getLogger(__name__)


def _delete_old_trashed_files() -> int:
    """
    Delete trashed files after 30 days.
    """
    count = 0
    for path in track.list_tracks_recursively(settings.music_dir, trashed=True):
        if path.stat().st_ctime < time.time() - 60 * 60 * 24 * 30:
            log.info("Permanently deleting: %s", path.absolute().as_posix())
            path.unlink()
            count += 1
    return count


async def cleanup() -> None:
    """
    Invokes other cleanup functions
    """
    count = await auth.prune_old_session_tokens()
    log.info("Deleted %s session tokens", count)

    count = _delete_old_trashed_files()
    log.info("Deleted %s trashed files", count)
