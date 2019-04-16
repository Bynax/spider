# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os

from items import NeighborHotel, CommentItem, PersonItem, HotelItem


class SpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'hotel_url':
            name = item['city_name']
            print("写入{}".format(name))
            with open("hotel_links/{}_hotels.txt".format(name), "a+", encoding="utf-8")as f:
                f.write(item['hotel_link'] + "\n")
            return item
        elif spider.name == 'city_url':
            line = json.dumps(dict(item)) + "\n"
            with open('{}.json'.format(spider.name), "a+", encoding="utf-8")as f:
                f.write(line)
            return item
        # 其他的字段都是表，写入csv文件
        elif spider.name == 'hotel_detail':
            if isinstance(item, NeighborHotel):
                file_name = 'neighbor.json'
            elif isinstance(item, CommentItem):
                file_name = 'comment.json'
            elif isinstance(item, HotelItem):
                file_name = 'hotel,json'
            elif isinstance(item, PersonItem):
                file_name = 'person.json'
            else:
                return item
            with open(os.path.join(os.path.abspath(os.path.join(os.getcwd(), "../..")), 'data/{}'.format(file_name)),
                      'a+', encoding='utf-8')as f:
                line = json.dumps(dict(item)) + "\n"
                f.write(line)

                return item
        else:
            return item
