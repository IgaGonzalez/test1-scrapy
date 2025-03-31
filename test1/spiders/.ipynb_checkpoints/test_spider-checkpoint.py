import scrapy

class TestSpider(scrapy.Spider):
    name = "test_spider"
    start_urls = ["http://httpbin.org/ip"]

    def parse(self, response):
        self.logger.info("TestSpider has crawled: %s", response.url)
