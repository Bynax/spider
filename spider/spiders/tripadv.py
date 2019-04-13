# -*- coding: utf-8 -*-
from scrapy import Request, Spider
import scrapy
import re

pre_url = 'https://www.tripadvisor.cn'


class TripadvSpider(Spider):
    name = 'tripadv'  # 爬虫名
    allowed_domains = ['tripadvisor.cn']  # 允许爬取的范围
    start_urls = ['http://tripadvisor.cn/']  # 最开始请求的url地址

    def start_requests(self):
        hotel_detail_url = "/Hotel_Review-g294212-d595677-Reviews-Park_Plaza_Wangfujing-Beijing.html"
        yield Request(hotel_detail_url, callback=self.parse_detail_hotel)

    def parse_detail_hotel(self, response):
        xpath_hotel_name_cn = '//*[@id="HEADING"]/text()'  # 酒店名称
        xpath_hotel_name_en = '//*[@id="HEADING"]/div/text()'  # 英文名称
        xpath_youhui = '//*[@id="taplc_resp_hr_atf_meta_0"]/div/div/div/div[4]/div[1]/div[1]'  # 不确定
        xpath_rank = '//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span/b/text()'  # 酒店排名
        xpath_comment_num = '//*[@id="REVIEWS"]/div[1]/div/div[1]/span/text()'  # 评论数量
        xpath_grade = '//*[@id="OVERVIEW"]/div[2]/div[1]/div/span[1]/text()'  # 酒店分数 1-5
        xpath_address = '//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[2]/div/div[2]/div/div/span[2]/span[2]/text()'  # 地址
        xpath_pics_num = '//*[@id="component_12"]/div/div[1]/div/div[1]/div/div[5]/div/div/span[3]/text()'  # 照片张数,两个括号一个数字
        xpath_feature = '//*[@id="ABOUT_TAB"]/div[2]/div[2]/div/div/div[2]/div[2]/div/div/text()'  # 酒店特色
        xpath_star = '//*[@id="OVERVIEW"]/div[2]/div[4]/div[2]/div/div[2]/div[3]/div/text()'  # 酒店星级
        # xpath_rooms = scrapy.Field()  # 房间数
        # xpath_url = scrapy.Field()  # 酒店官网
        xpath_room_type = '//*[@id="ABOUT_TAB"]/div[2]/div[4]/div[2]/div[6]/div/text()'  # 客房类型
        xpath_award = scrapy.Field()  # 奖项


if __name__ == '__main__':
    with open("../../hotel_links/Beijing_hotels.txt", "r+", encoding="utf-8")as f:
        print(f.name)
