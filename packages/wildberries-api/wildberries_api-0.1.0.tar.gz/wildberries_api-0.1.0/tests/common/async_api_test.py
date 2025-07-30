from tests.fake_async_session import FakeAsyncSession
from wb_api.common.async_api import AsyncCommonAPI

from unittest.mock import patch, Mock

import pytest


class TestAsyncCommonAPI:
	@pytest.mark.asyncio()
	async def test_ping(self):
		session = FakeAsyncSession("RAW DATA")
		api = AsyncCommonAPI(session)		# type: ignore - for testing purposes

		with patch("wb_api.common.async_api.PingResponse") as PingResponseMock:
			PingResponseMock.model_validate_json = Mock()
			PingResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.ping() == "DESERIALIZED DATA"
				PingResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://common-api.wildberries.ru/ping"
