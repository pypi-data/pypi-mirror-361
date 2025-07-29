from ya_market_api.feedback.base_api import BaseFeedbackAPI
from ya_market_api.exception import BusinessIdError

import pytest


class TestBaseFeedbackAPI:
	def test_business_id(self):
		api = BaseFeedbackAPI()

		with pytest.raises(BusinessIdError, match="The business_id was not specified"):
			api.business_id

		api = BaseFeedbackAPI(512)
		assert api.business_id == 512
