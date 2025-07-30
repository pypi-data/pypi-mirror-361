from wb_api.async_api import AsyncAPI
from wb_api.common.async_api import AsyncCommonAPI
from wb_api.feedback.async_api import AsyncFeedbackAPI
from wb_api.const import Header

import pytest
from aiohttp.client import ClientSession


class TestAsyncAPI:
	@pytest.mark.asyncio()
	async def test___init__(self):
		session = ClientSession()
		api = AsyncAPI(session)
		assert api.session is session
		assert isinstance(api.common, AsyncCommonAPI)
		assert api.common.session is session
		assert isinstance(api.feedback, AsyncFeedbackAPI)
		assert api.feedback.session is session

	@pytest.mark.asyncio()
	async def test_build(self):
		api = await AsyncAPI.build("ACCESS_TOKEN")
		assert api.session.headers[Header.AUTHORIZATION.value] == "ACCESS_TOKEN"

	@pytest.mark.asyncio()
	async def test_make_session(self):
		session = await AsyncAPI.make_session(token="ACCESS_TOKEN")
		assert session.headers == {Header.AUTHORIZATION.value: "ACCESS_TOKEN"}
