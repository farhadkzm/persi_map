import scrapy


class NamesSpider(scrapy.Spider):
    name = "healthpages.wiki_names"
    start_urls = [
        'https://healthpages.wiki/wiki/Special:BrowseData/Healthcare_Professional?_single&Occupation=General_Practitioner_%28GP%29&State=VIC',
    ]
    pages = 20

    def parse(self, response):
        self.pages -= 1
        if self.pages == 0:
            return
        for item in response.xpath('//*[@id="mw-content-text"]//ul/li[@data-sortkey]'):
            yield {"link": response.urljoin(item.xpath('a/@href').extract_first())}

        next_page = response.xpath('//a[@class="mw-nextlink"]/@href').extract_first()

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
