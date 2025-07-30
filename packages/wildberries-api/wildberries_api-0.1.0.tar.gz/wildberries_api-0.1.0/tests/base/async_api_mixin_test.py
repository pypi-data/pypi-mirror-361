from wb_api.base.async_api_mixin import AsyncAPIMixin
from wb_api.exception import InvalidResponseError

from unittest.mock import Mock
from http import HTTPStatus

import pytest
from aiohttp.client import ClientSession


class TestAsyncAPIMixin:
	@pytest.mark.asyncio()
	async def test_validate_response(self):
		session = ClientSession()
		api = AsyncAPIMixin(session)
		response = Mock()
		response.status = HTTPStatus.OK
		assert api.validate_response(response) is None

		response.status = HTTPStatus.FORBIDDEN

		with pytest.raises(InvalidResponseError, match="Response is not valid"):
			api.validate_response(response)

		assert api.validate_response(response, HTTPStatus.FORBIDDEN) is None
