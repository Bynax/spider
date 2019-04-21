# -*- coding: utf-8 -*-
from scrapy import Request, Spider
from spider.items import CityItem
import re

# 51页的时候是20*50

# def


# 固定爬取50页的城市
page_num = 100
# page_num = 2
tempelt = "https://www.tripadvisor.cn/Hotels-g294211-oa{}-China-Hotels.html"
prefix = "https://www.tripadvisor.cn"


def parse_city_id(url):
    return re.findall('g\d+(?=-)', url)[0]


class CityUrlSpider(Spider):
    name = 'city_url'
    allowed_domains = ['tripadvisor.cn']
    start_urls = ['http://tripadvisor.cn/']

    def start_requests(self):
        city_urls = []
        for i in range(1, page_num):
            city_urls.append(tempelt.format(20 * i))
        return [Request(city_url, self.parse, meta={'max': 3}) for city_url in
                city_urls]

    def parse(self, response):
        # page_num = response.meta['page_num']
        # if int(page_num) == 0:
        #     links = response.xpath(r'//div[@class="geo_wrap"]/a/@href').extract()
        #     print(links)
        #     for link in links:
        #         yield Request(url='{}{}'.format(prefix, link), callback=self.parse_city_detail)

        links = response.xpath(
            r'//*[@id="taplc_broad_geo_tiles_dusty_hotels_resp_0"]/ul/li/a/@href').extract()

        for link in links:
            yield Request(url='{}{}'.format(prefix, link), callback=self.parse_city_detail)


    def parse_city_detail(self, response):
        city = CityItem()
        city_id = parse_city_id(response.request.url)
        city['city_id'] = city_id if city_id is not None else 'N/A'
        city_name = response.xpath(
            '//*[@id="taplc_trip_planner_breadcrumbs_0"]/ul/li[4]/a/span/text()').extract_first()
        city['city_name'] = city_name if city_name is not None else 'N/A'
        province = response.xpath(
            '//*[@id="taplc_trip_planner_breadcrumbs_0"]/ul/li[3]/a/span/text()').extract_first()

        city['province'] = province if province is not None else 'N/A'
        raw_hotel_num = response.xpath(
            '//*[@id="taplc_dh_sort_filter_entry_0"]/div[2]/div/span/span').extract_first()
        # yield city

        hotel_num = "".join(re.findall('[0-9]', raw_hotel_num))
        city['hotel_num'] = hotel_num if hotel_num is not None else 'N/A'
        yield city

        print('{},{},{},{}'.format(city['city_id'], city['city_name'], city['province'], city['hotel_num']))

if __name__ == '__main__':
    for i in range(100,200):
        print(i)