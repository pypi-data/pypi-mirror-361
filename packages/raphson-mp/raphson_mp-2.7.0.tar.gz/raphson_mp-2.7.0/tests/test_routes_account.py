from tests import T_client, assert_html


async def test_account(client: T_client):
    await assert_html(client, "/account")
