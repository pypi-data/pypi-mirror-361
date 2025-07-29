from ya_market_api.guide.region.router import GuideRegionRouter


class TestGuideRegionRouter:
	def test_region_countries(self):
		router = GuideRegionRouter()
		assert router.region_countries() == "https://api.partner.market.yandex.ru/regions/countries"

	def test_region_search(self):
		router = GuideRegionRouter()
		assert router.region_search() == "https://api.partner.market.yandex.ru/regions"

	def test_region_info(self):
		router = GuideRegionRouter()
		assert router.region_info(512) == "https://api.partner.market.yandex.ru/regions/512"

	def test_region_children(self):
		router = GuideRegionRouter()
		assert router.region_children(512) == "https://api.partner.market.yandex.ru/regions/512/children"
