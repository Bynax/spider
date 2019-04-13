# -*- coding: utf-8 -*-
import scrapy
import json
import re
from spider.items import HotelLinkItem

# 给定城市，爬取固定页数该城市的宾馆
prefix = "https://www.tripadvisor.cn"

page_limit = 3


class HotelUrlSpider(scrapy.Spider):
    name = 'hotel_url'
    allowed_domains = ['tripadvisor.cn']

    def __init__(self):
        with open("a.json", "r+", encoding="utf-8")as f:
            self.source_data = json.loads("".join(f.readlines()))

    def start_requests(self):
        for data in self.source_data:
            for (k, v) in data.items():
                if k == 'urls':
                    for url in v:
                        url = prefix + url
                        yield scrapy.Request(url=url, callback=self.parse_initial)  # 定义errorback字段，自定义出错函数

    def parse_initial(self, response):
        div = response.xpath('//*[@class="pageNumbers"]/a')
        if div is None:
            return 1
        page_num = int(response.xpath('//*[@class="pageNumbers"]/a/@data-page-number').extract()[-1])
        page_num = page_limit if page_num > page_limit else page_num
        url_start = re.search('.+\d+', response.request.url, re.M | re.I)

        # 生成下几页请求并返回
        for i in range(1, page_num):
            page_url = re.sub('.+\d+', url_start.group() + '-oa' + str(i * 30), response.request.url)
            yield scrapy.Request(page_url, callback=self.parse)

        # 返回item
        hotel_link = response.xpath('//*[@class="listing_title"]/a/@href').extract()
        for link in hotel_link:
            city_name = re.findall('(?<=\d-).*?(?=-)', response.request.url)[0]
            hotel_link_item = HotelLinkItem()
            hotel_link_item['city_name'] = city_name
            hotel_link_item['hotel_link'] = link
            yield hotel_link_item

    def parse(self, response):

        hotel_link = response.xpath('//*[@class="listing_title"]/a/@href').extract()
        for link in hotel_link:
            city_name = re.findall('(?<=\d-).*?(?=-)', response.request.url)[1]
            hotel_link_item = HotelLinkItem()
            hotel_link_item['city_name'] = city_name
            hotel_link_item['hotel_link'] = link
            yield hotel_link_item


