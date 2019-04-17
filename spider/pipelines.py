# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import six
import pymysql as pq  # 导入pymysql

from spider.items import NeighborHotel, CommentItem, PersonItem, HotelItem
from scrapy.utils.project import get_project_settings


class SpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWriterPipeline(object):
    def __init__(self):
        setting = get_project_settings()
        '''
        MYSQL_HOST = 
MYSQL_DBNAME 
MYSQL_USER = 
MYSQL_PASSWD 
MYSQL_PORT = 
        '''

        self.conn = pq.connect(host=setting.get('MYSQL_HOST'), user=setting.get('MYSQL_USER'),
                               port=setting.get('MYSQL_PORT'),
                               passwd=setting.get('MYSQL_PASSWD'), db=setting.get('MYSQL_DBNAME'), charset='utf8')
        self.cur = self.conn.cursor()

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
                table_name = 'neighbor'
            elif isinstance(item, CommentItem):
                table_name = 'comment'
            elif isinstance(item, HotelItem):
                table_name = 'hotel'
            elif isinstance(item, PersonItem):
                table_name = 'person'
            else:
                return item

            col_str = ''
            row_str = ''
            for key in item.keys():
                col_str = col_str + " " + key + ","
                row_str = "{}'{}',".format(row_str,
                                           item[key] if "'" not in item[key] else item[key].replace("'", "\\'"))
                sql = 'insert INTO {} ({}) VALUES ({}) ON DUPLICATE KEY UPDATE '.format(table_name, col_str[1:-1],
                                                                                        row_str[:-1])
            for (key, value) in six.iteritems(item):
                sql += "{} = '{}', ".format(key, value if "'" not in value else value.replace("'", "\\'"))
            sql = sql[:-2]
            self.cur.execute(sql)  # 执行SQL
            self.conn.commit()  # 写入操作
            # with io.open(os.path.join(os.path.abspath(os.getcwd()), 'data/{}'.format(file_name)),
            #              'a+', encoding='utf-8')as f:
            #     line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            #     f.write(line)

            return item
        else:
            return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()


if __name__ == '__main__':
    setting = get_project_settings()
