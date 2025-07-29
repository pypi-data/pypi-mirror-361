import asyncio
import secrets
from pathlib import Path
import tracemalloc

from aiohttp import web
from aiohttp.test_utils import TestClient

from raphson_mp import auth, db, logconfig, settings

T_client = TestClient[web.Request, web.Application]

TEST_USERNAME: str = "autotest"
TEST_PASSWORD: str = secrets.token_urlsafe()


def set_dirs():
    settings.data_dir = Path("./data").resolve()
    settings.music_dir = Path("./music").resolve()


def setup_module():
    set_dirs()
    settings.log_warnings_to_file = True
    settings.log_level = "DEBUG"
    logconfig.apply()

    with db.connect() as conn:
        conn.execute("DELETE FROM user WHERE username = ?", (TEST_USERNAME,))

    asyncio.run(auth.User.create(TEST_USERNAME, TEST_PASSWORD))

    tracemalloc.start()


async def get_csrf(client: T_client):
    async with client.get("/auth/get_csrf") as response:
        assert response.status == 200, await response.text()
        return (await response.json())["token"]


async def assert_html(client: T_client, url: str):
    async with client.get(url) as response:
        response.raise_for_status()
        assert response.content_type == 'text/html'
        # make sure the template has rendered completely to the end without errors
        assert (await response.text()).endswith("</html>")
