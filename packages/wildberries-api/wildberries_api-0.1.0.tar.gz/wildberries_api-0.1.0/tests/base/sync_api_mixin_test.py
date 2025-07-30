from wb_api.base.sync_api_mixin import SyncAPIMixin
from wb_api.exception import InvalidResponseError

from unittest.mock import Mock
from http import HTTPStatus

import pytest
from requests.sessions import Session


class TestSyncAPIMixin:
	@pytest.mark.asyncio()
	async def test_validate_response(self):
		session = Session()
		api = SyncAPIMixin(session)
		response = Mock()
		response.status_code = HTTPStatus.OK
		assert api.validate_response(response) is None

		response.status_code = HTTPStatus.FORBIDDEN

		with pytest.raises(InvalidResponseError, match="Response is not valid"):
			api.validate_response(response)

		assert api.validate_response(response, HTTPStatus.FORBIDDEN) is None
