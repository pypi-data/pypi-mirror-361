from tests import T_client, assert_html


async def test_player(client: T_client):
    await assert_html(client, "/player")
