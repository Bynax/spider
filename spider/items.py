# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HotelLinkItem(scrapy.Item):
    city_name = scrapy.Field()
    hotel_link = scrapy.Field()


# page 表示是第几页 urls是一个列表，表示该页所有的url
class PageItem(scrapy.Item):
    page = scrapy.Field()
    urls = scrapy.Field()


class CityItem(scrapy.Item):
    # 城市编号自动生成/点评总数量最后统计 这两个字段不能爬取
    city_id = scrapy.Field()
    city_name = scrapy.Field()  # 城市名称
    province = scrapy.Field()  # 所属省份
    hotel_num = scrapy.Field()  # 酒店总数量


class HotelItem(scrapy.Item):
    # 酒店id
    hotel_id = scrapy.Field()
    hotel_city = scrapy.Field()
    hotel_name_cn = scrapy.Field()  # 酒店名称
    hotel_name_en = scrapy.Field()  # 英文名称
    youhui = scrapy.Field()  # 优惠价钱和网站
    rank = scrapy.Field()  # 酒店排名
    comment_num = scrapy.Field()  # 评论数量
    grade = scrapy.Field()  # 酒店分数 1-5
    address = scrapy.Field()  # 地址
    pics_num = scrapy.Field()  # 照片张数
    feature = scrapy.Field()  # 酒店特色
    style = scrapy.Field()
    star = scrapy.Field()  # 酒店星级
    rooms = scrapy.Field()  # 房间数
    room_type = scrapy.Field()  # 客房类型
    award = scrapy.Field()  # 奖项


class CommentItem(scrapy.Item):
    hotel_id = scrapy.Field()  # 所属酒店id
    title = scrapy.Field()
    comment_id = scrapy.Field()
    comment_date = scrapy.Field()  # 评论时间
    person = scrapy.Field()  # 评论人id
    content = scrapy.Field()  # 评论内容
    reply = scrapy.Field()  # 回复内容
    rating = scrapy.Field()


class PersonItem(scrapy.Item):  # 评论人
    person_id = scrapy.Field()
    grade = scrapy.Field()
    gender = scrapy.Field()
    description = scrapy.Field()
    age = scrapy.Field()
    member_type = scrapy.Field()
    review_total_num = scrapy.Field()
    visited_city_num = scrapy.Field()
    photo_nums = scrapy.Field()
    userfule_votes = scrapy.Field()
    review_dis = scrapy.Field()


class NeighborHotel(scrapy.Item):  # 附近酒店
    hotel_id = scrapy.Field()  # 酒店id
    target_id = scrapy.Field()  # 距离酒店的id
    distance = scrapy.Field()  # 距离
