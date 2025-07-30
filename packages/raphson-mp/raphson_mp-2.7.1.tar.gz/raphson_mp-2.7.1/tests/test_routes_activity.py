from tests import T_client, assert_html


async def test_activity(client: T_client):
    await assert_html(client, "/activity")


async def test_files(client: T_client):
    await assert_html(client, "/activity/files")


async def test_all(client: T_client):
    await assert_html(client, "/activity/all")
