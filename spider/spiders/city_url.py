# -*- coding: utf-8 -*-
from scrapy import Request, Spider
from spider.items import PageItem



# 51页的时候是20*50

# def


# https://www.tripadvisor.cn/Hotels-g294211-oa1000-China-Hotels.html
# https://www.tripadvisor.cn/Hotels-g294211-oa940-China-Hotels.html


# 固定爬取50页的城市
page_num = 51
# page_num = 2
tempelt = "https://www.tripadvisor.cn/Hotels-g294211-oa{}-China-Hotels.html"


class CityUrlSpider(Spider):
    name = 'city_url'
    allowed_domains = ['tripadvisor.cn']
    start_urls = ['http://tripadvisor.cn/']

    def start_requests(self):
        first_url = "https://www.tripadvisor.cn/Hotels-g294211-China-Hotels.html"
        city_urls = [first_url]
        for i in range(1, page_num):
            city_urls.append(tempelt.format(20 * i))
        return [Request(city_url, self.parse, meta={'page_num': city_urls.index(city_url)}) for city_url in city_urls]

    def parse(self, response):
        urls = PageItem()
        urls['page'] = response.meta['page_num']
        if int(urls['page']) == 0:
            urls['urls'] = response.xpath(r'//div[@class="geo_wrap"]/a/@href').extract()
        else:
            urls['urls'] = response.xpath(
                r'//*[@id="taplc_broad_geo_tiles_dusty_hotels_resp_with_pagination_optimization_0"]/ul/li/a/@href').extract()
        yield urls
