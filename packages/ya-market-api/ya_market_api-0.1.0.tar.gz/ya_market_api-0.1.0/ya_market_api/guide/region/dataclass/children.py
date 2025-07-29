from ya_market_api.guide.region.dataclass.region import Region

from typing import Optional

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.functional_validators import field_validator


class Request(BaseModel):
	region_id: int
	page: Optional[int] = None
	page_size: Optional[int] = Field(default=None, serialization_alias="pageSize")

	@field_validator("page", mode="after")
	@classmethod
	def page_is_valid(cls, value: Optional[int]) -> Optional[int]:
		if value is None:
			return None

		if value < 1 or value > 10_000:
			raise ValueError("The page cannot be less than 1 or greater than 10000")

		return value

	@field_validator("page_size", mode="after")
	@classmethod
	def page_size_is_valid(cls, value: Optional[int]) -> Optional[int]:
		if value is None:
			return None

		if value < 1:
			raise ValueError("The page_size cannot be less than 1")

		return value


class ResponsePager(BaseModel):
	current_page: Optional[int] = Field(None, validation_alias="currentPage")
	from_: Optional[int] = Field(None, validation_alias="from")
	page_size: Optional[int] = Field(None, validation_alias="pageSize")
	page_count: Optional[int] = Field(None, validation_alias="pageCount")
	to: Optional[int] = None
	total: Optional[int] = None


class Response(BaseModel):
	pager: Optional[ResponsePager] = None
	region: Optional[Region] = Field(default=None, validation_alias="regions")
