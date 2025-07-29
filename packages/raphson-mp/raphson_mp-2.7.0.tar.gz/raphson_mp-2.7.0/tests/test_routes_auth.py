from tests import T_client, assert_html


async def test_login(client: T_client):
    await assert_html(client, "/auth/login")


async def test_get_csrf(client: T_client):
    async with client.get("/auth/get_csrf") as response:
        json = await response.json()
        assert "token" in json
