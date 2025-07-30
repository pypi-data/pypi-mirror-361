import hashlib
import random
import secrets
import time
from typing import cast
from raphson_mp import activity, db
from raphson_mp.common.music import Album, Artist
from raphson_mp.routes import subsonic
from raphson_mp.routes.subsonic import from_id, to_id
from tests import TEST_USERNAME, T_client


def _token() -> str:
    with db.connect(read_only=True) as conn:
        (token,) = conn.execute(
            "SELECT token FROM session JOIN user ON session.user = user.id WHERE username = ? LIMIT 1", (TEST_USERNAME,)
        ).fetchone()
    return token


async def test_auth(client: T_client):
    token = _token()

    # No authentication
    async with client.get("/rest/ping") as response:
        response.raise_for_status()
        assert '<error code="42" />' in await response.text()

    # API key authentication
    async with client.get("/rest/ping", params={"apiKey": token}) as response:
        response.raise_for_status()
        assert 'status="ok"' in await response.text()
    async with client.get("/rest/ping", params={"apiKey": token, "u": "something"}) as response:
        response.raise_for_status()
        assert '<error code="43" />' in await response.text()
    async with client.get("/rest/ping", params={"apiKey": secrets.token_hex()}) as response:
        response.raise_for_status()
        assert '<error code="44" />' in await response.text()

    # Legacy authentication
    async with client.get("/rest/ping", params={"u": TEST_USERNAME, "p": token}) as response:
        response.raise_for_status()
        assert 'status="ok"' in await response.text()
    async with client.get("/rest/ping", params={"u": TEST_USERNAME, "p": "enc:" + token.encode().hex()}) as response:
        response.raise_for_status()
        assert 'status="ok"' in await response.text()
    async with client.get("/rest/ping", params={"u": TEST_USERNAME, "p": token + "a"}) as response:
        response.raise_for_status()
        assert '<error code="40" />' in await response.text()

    # Hashed token authentication
    salt = secrets.token_hex()
    hash = hashlib.md5((token + salt).encode()).hexdigest()
    async with client.get("/rest/ping", params={"u": TEST_USERNAME, "t": hash, "s": salt}) as response:
        response.raise_for_status()
        assert 'status="ok"' in await response.text()
    async with client.get("/rest/ping", params={"u": TEST_USERNAME, "t": hash, "s": salt + "a"}) as response:
        response.raise_for_status()
        assert '<error code="40" />' in await response.text()


async def _request(client: T_client, endpoint: str, params: dict[str, str]):
    async with client.get(
        "/rest/" + endpoint, params={"apiKey": _token(), "f": "json", "c": "Test", **params}
    ) as response:
        response.raise_for_status()
        return response


async def _request_json(client: T_client, endpoint: str, params: dict[str, str]):
    async with client.get(
        "/rest/" + endpoint, params={"apiKey": _token(), "f": "json", "c": "Test", **params}
    ) as response:
        response.raise_for_status()
        return (await response.json())["subsonic-response"]


async def test_id(track: str, artist: Artist, album: Album, playlist: str):
    assert from_id(to_id(track)) == track
    assert from_id(to_id(artist)) == artist
    assert from_id(to_id(album)) == album
    assert from_id(to_id(playlist)) == playlist


async def test_getOpenSubsonicExtensions(client: T_client):
    await _request_json(client, "getOpenSubsonicExtensions", {})


async def test_getArtists(client: T_client):
    await _request(client, "getArtists", {})


async def test_getArtist(client: T_client, artist: Artist):
    artist_id = to_id(artist)
    response = await _request_json(client, "getArtist", {"id": artist_id})
    assert cast(Artist, from_id(response["artist"]["id"])).name == artist.name
    assert response["artist"]["name"] == artist.name
    assert response["artist"]["coverArt"] == response["artist"]["id"]


async def test_getAlbumList2(client: T_client):
    await _request_json(client, "getAlbumList2", {"type": "random"})
    await _request_json(client, "getAlbumList2", {"type": "newest"})
    await _request_json(client, "getAlbumList2", {"type": "highest"})
    await _request_json(client, "getAlbumList2", {"type": "frequent"})
    await _request_json(client, "getAlbumList2", {"type": "recent"})
    await _request_json(client, "getAlbumList2", {"type": "byYear", "fromYear": "2000", "toYear": "2010"})
    await _request_json(client, "getAlbumList2", {"type": "byGenre", "genre": "Pop"})
    await _request_json(client, "getAlbumList2", {"type": "alphabeticalByName"})
    await _request_json(client, "getAlbumList2", {"type": "alphabeticalByArtist"})


async def test_getCoverArt_album(client: T_client, album: Album):
    await _request(client, "getCoverArt", {"id": to_id(album)})


async def test_getCoverArt_track(client: T_client, track: str):
    await _request(client, "getCoverArt", {"id": to_id(track)})


async def test_getAlbum(client: T_client, album: Album):
    album_id = to_id(album)
    response = await _request_json(client, "getAlbum", {"id": album_id})
    assert cast(Album, from_id(response["album"]["id"])).name == album.name
    assert cast(Album, from_id(response["album"]["id"])).artist == album.artist
    assert response["album"]["name"] == album.name
    assert response["album"]["coverArt"] == response["album"]["id"]
    assert response["album"]["songCount"] >= 1
    assert response["album"]["duration"] > 10
    assert response["album"]["sortName"]
    assert isinstance(response["album"]["isCompilation"], bool)


async def test_getSong(client: T_client, track: str):
    response = await _request_json(client, "getSong", {"id": to_id(track)})
    assert cast(str, from_id(response["song"]["id"])) == track
    assert response["song"]["isDir"] == False
    assert response["song"]["duration"] > 10


async def test_stream(client: T_client, track: str):
    await _request(client, "stream", {"id": to_id(track)})


async def test_download(client: T_client, track: str):
    await _request(client, "stream", {"id": to_id(track)})


async def test_getLyrics():
    # TODO
    pass


async def test_getLyricsBySongId(client: T_client, track: str):
    await _request_json(client, "getLyricsBySongId", {"id": to_id(track)})
    # TODO verify response contents


async def test_search3(client: T_client):
    await _request_json(client, "search3", {"query": "test"})


async def test_search3_all(client: T_client):
    await _request_json(client, "search3", {"query": ""})


async def test_getPlaylists(client: T_client):
    await _request_json(client, "getPlaylists", {})


async def test_getPlaylist(client: T_client, playlist: str):
    await _request_json(client, "getPlaylist", {"id": to_id(playlist)})


async def test_scrobble(client: T_client, track: str):
    await _request_json(client, "scrobble", {"id": to_id(track)})
    now_playing_list = activity.now_playing()
    for now_playing in now_playing_list:
        if now_playing.data.track is not None and now_playing.data.track == track:
            break
    else:
        assert False, now_playing_list

    # test that no history entry is created when submission is set to false
    with db.connect(read_only=True) as conn:
        row = conn.execute("SELECT timestamp FROM history ORDER BY timestamp DESC LIMIT 1").fetchone()
        assert row is None or row[0] < time.time() - 1


async def test_scrobble_submission(client: T_client, track: str):
    await _request_json(client, "scrobble", {"id": to_id(track), "submission": "true"})

    # a history entry should be created now
    with db.connect(read_only=True) as conn:
        row = conn.execute("SELECT track, timestamp FROM history ORDER BY timestamp DESC LIMIT 1").fetchone()
        assert row is not None
        assert row[0] == track
        assert row[1] > time.time() - 1


async def test_getRandomSongs(client: T_client):
    response = await _request_json(client, "getRandomSongs", {"size": "5"})
    assert len(response["randomSongs"]["song"]) == 5


async def test_getRandomSongs_fromYear(client: T_client):
    year = random.randint(1980, 2020)
    response = await _request_json(client, "getRandomSongs", {"fromYear": str(year)})
    for song in response["randomSongs"]["song"]:
        assert song["year"] >= year


async def test_getRandomSongs_toYear(client: T_client):
    year = random.randint(1980, 2020)
    response = await _request_json(client, "getRandomSongs", {"toYear": str(year)})
    for song in response["randomSongs"]["song"]:
        assert song["year"] <= year


async def test_getGenres(client: T_client):
    response = await _request_json(client, "getGenres", {})
    assert isinstance(response["genres"]["genre"], list)


async def test_getSongsByGenre(client: T_client):
    with db.connect(read_only=True) as conn:
        track, tag = conn.execute("SELECT track, tag FROM track_tag LIMIT 1").fetchone()

    response = await _request_json(client, "getSongsByGenre", {"genre": tag})
    for song in response["songsByGenre"]["song"]:
        if cast(str, from_id(song["id"])) == track:
            break
    else:
        assert False, response["songsByGenre"]["song"]


async def test_getStarred(client: T_client):
    response = await _request_json(client, "getStarred", {})
    assert response["starred"]["artist"] == []
    assert response["starred"]["album"] == []
    assert response["starred"]["song"] == []


async def test_getStarred2(client: T_client):
    response = await _request_json(client, "getStarred2", {})
    assert response["starred2"]["artist"] == []
    assert response["starred2"]["album"] == []
    assert response["starred2"]["song"] == []


async def test_getArtistInfo2(client: T_client):
    response = await _request_json(client, "getArtistInfo2", {})
    assert response["artistInfo2"] == {}


async def test_getAlbumInfo2(client: T_client):
    response = await _request_json(client, "getAlbumInfo2", {})
    assert response["albumInfo2"] == {}


async def test_getLicense(client: T_client):
    response = await _request_json(client, "getLicense", {})
    assert response["license"]["valid"] is True


async def test_getSimilarSongs2_track(client: T_client, track: str):
    await _request_json(client, "getSimilarSongs2", {"id": to_id(track)})


async def test_getSimilarSongs2_artist(client: T_client, artist: Artist):
    await _request_json(client, "getSimilarSongs2", {"id": to_id(artist)})


async def test_tokenInfo(client: T_client):
    response = await _request_json(client, "tokenInfo", {})
    assert response["tokenInfo"]["username"] == TEST_USERNAME


async def test_startScan(client: T_client):
    pass
    response = await _request_json(client, "startScan", {})
    assert isinstance(response["scanStatus"]["scanning"], bool)
    assert isinstance(response["scanStatus"]["count"], int)
    assert subsonic.scan_task
    # wait for scanner to finish, or errors occur
    await subsonic.scan_task


async def test_getScanStatus(client: T_client):
    response = await _request_json(client, "getScanStatus", {})
    assert response["scanStatus"]["scanning"] is False
    assert isinstance(response["scanStatus"]["count"], int)
