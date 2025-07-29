from pathlib import Path

from raphson_mp import db
from raphson_mp.common.track import is_trashed
from raphson_mp.track import filter_tracks


def test_is_trashed():
    assert not is_trashed(Path("test"))
    assert is_trashed(Path(".trash.test"))
    assert is_trashed(Path(".trash.test/test"))


def test_filter_tracks():
    # not a functional test, but ensures SQL has no syntax error
    with db.connect() as conn:
        for order in [None, "title", "ctime", "year", "random", "title,year"]:
            for has_metadata in [False, True]:
                filter_tracks(
                    conn,
                    10,
                    0,
                    playlist="test",
                    artist="test",
                    album_artist="test",
                    album="test",
                    year=1000,
                    has_metadata=has_metadata,
                    order=order,
                )
