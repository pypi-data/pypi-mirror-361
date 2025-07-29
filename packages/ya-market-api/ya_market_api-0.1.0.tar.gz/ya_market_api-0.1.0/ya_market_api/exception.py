class APIError(Exception):
	"""
	Base API error class.
	"""
	pass


class InvalidResponseError(APIError):
	pass


class BusinessIdError(APIError):
	pass
