# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json


class SpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'hotel_url':
            name = item['city_name']
            with open("hotel_links/{}_hotels.txt".format(name), "a+", encoding="utf-8")as f:
                f.write(item['hotel_link'] + "\n")
            return item
        elif spider.name == 'city_url':
            line = json.dumps(dict(item)) + "\n"
            with open('{}.json'.format(spider.name), "w", encoding="utf-8")as f:
                f.write(line)
            return item
        elif spider.name == '':
            pass
            return item
        else:
            return item

    # def open_spider(self, spider):
    #     self.file = open('{}.json'.format(spider.name), 'w')
    #
    # def close_spider(self, spider):
    #     self.file.close()
    #
    # def process_item(self, item, spider):
    #     line = json.dumps(dict(item)) + "\n"
    #     self.file.write(line)
    #     return item
