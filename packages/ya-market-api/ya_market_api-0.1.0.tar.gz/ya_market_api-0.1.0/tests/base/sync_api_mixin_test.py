from ya_market_api.base.sync_api_mixin import SyncAPIMixin
from ya_market_api.exception import InvalidResponseError

from http import HTTPStatus

import pytest
from requests.sessions import Session
from requests.models import Response


class TestSyncAPIMixin:
	def test_validate_response(self):
		api = SyncAPIMixin(Session())
		response = Response()
		response.status_code = HTTPStatus.OK
		assert api.validate_response(response) is None

		response.status_code = HTTPStatus.FORBIDDEN

		with pytest.raises(InvalidResponseError, match="Response is not valid"):
			api.validate_response(response)
