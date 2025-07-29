from raphson_mp import cleanup
from raphson_mp.common.track import TRASH_PREFIX
from raphson_mp.track import from_relpath


async def test_delete_trash(playlist: str):
    test_path = from_relpath(f"{playlist}/{TRASH_PREFIX}test_file")
    test_path.touch()
    assert test_path.is_file()

    # file should not be deleted
    cleanup._delete_old_trashed_files()
    assert test_path.is_file()

    # we cannot test if an old file will be deleted, it is not possible to change the file ctime
    # mtime cannot be used because it does not change when a file is moved (trashed)

    test_path.unlink()
