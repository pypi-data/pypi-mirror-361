from datetime import datetime, timedelta, timezone
from multidict import CIMultiDict
from raphson_mp import db
from tests import T_client, assert_html


async def test_home(client: T_client):
    await assert_html(client, "/")


async def test_install(client: T_client):
    await assert_html(client, "/install")


async def test_pwa(client: T_client):
    async with client.get("/pwa") as response:
        response.raise_for_status()
        assert 'http-equiv="refresh"' in await response.text()


async def test_token(client: T_client):
    async with client.get("/token") as response:
        response.raise_for_status()
        token = await response.text()

    # make sure session is created
    with db.connect(read_only=True) as conn:
        conn.execute("SELECT 1 FROM session WHERE token = ?", (token,)).fetchone()


async def test_healthcheck(client: T_client):
    async with client.get("/health_check") as response:
        response.raise_for_status()
        assert await response.text() == "ok"


async def test_securitytxt(client: T_client):
    async with client.get("/.well-known/security.txt") as response:
        response.raise_for_status()

        values: CIMultiDict[str] = CIMultiDict()
        for line in (await response.content.read()).splitlines():
            key, value = line.split(b": ")
            values[key.decode()] = value.decode()

        assert "Contact" in values
        assert "Preferred-Languages" in values
        expires = datetime.fromisoformat(values["Expires"])
        # must be valid for at least another 30 days
        assert expires - datetime.now(tz=timezone.utc) > timedelta(days=30)
        # must not be valid for more than one year
        assert expires - datetime.now(tz=timezone.utc) < timedelta(days=365)
