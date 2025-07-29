from raphson_mp import radio, db


def test_clean_start():
    assert radio.current_track is None
    assert radio.next_track is None


async def test_choose_tracks():
    with db.connect(read_only=True) as conn:
        track = await radio.get_current_track(conn)
        assert track == radio.current_track
        track2 = await radio.get_current_track(conn)
        assert track == track2
        track3 = await radio.get_next_track(conn)
        assert track3
