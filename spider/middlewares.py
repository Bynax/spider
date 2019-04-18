# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from fake_useragent import UserAgent
import random
import os
import requests
import pymysql

current_proxy = 'http://a6d4348e218e:qwmcu5rqmi@222.218.222.70:8901'


class SpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgent(object):
    def __init__(self):
        self.proxy_files = os.path.join(os.path.abspath(os.getcwd()), 'proxies.txt')

    @staticmethod
    def get_proxies(self):
        with open(self.proxy_files, 'r+', encoding='utf-8')as f:
            return f.readlines()

    def process_request(self, request, spider):
        ua = UserAgent(verify_ssl=False)
        print("正在处理:{}".format(request.url))
        request.meta['proxy'] = current_proxy
        request.headers['User-Agent'] = ua.random
        if spider.name == 'review_detail':
            request.headers['x-requested-with'] = 'XMLHttpRequest'

    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            lines = self.get_proxies(self)
            if int(request.meta['max']) > 0:
                print('状态码非200')
                # 请求新的地址
                current_proxy = lines[random.randint(0, len(lines) - 1)].strip()
                # print("this is response ip:" + proxy)
                # 对当前reque加上代理
                request.meta['proxy'] = current_proxy
                print("更换代理为{}".format(current_proxy))
                request.meta['max'] = (int(request.meta['max'])) - 1
                return request
            else:
                raise IgnoreRequest("超过最大请求，{}\t被跳过".format(request.url))
        print("正常返回")
        return response

    def process_exception(self, request, exception, spider):
        # 出现异常时（超时）使用代理
        print("\n出现异常，正在使用代理重试....\n")
        if isinstance(exception,pymysql.DatabaseError):
            raise IgnoreRequest("数据库错误，不做处理")
        if request.meta['max'] > 0:
            lines = self.get_proxies(self)
            current_proxy = lines[random.randint(0, len(lines) - 1)].strip()
            # 对当前reque加上代理
            request.meta['proxy'] = current_proxy
            print("更换代理为{}".format(current_proxy))
            request.meta['max'] = (int(request.meta['max'])) - 1
            return request
        else:
            raise IgnoreRequest("超过最大请求，{}\t被跳过".format(request.url))


if __name__ == '__main__':
    proxies = {
        "http": "http://a6d4348e218e:qwmcu5rqmi@222.218.222.70:8901"
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'

    }

    res = requests.get(
        'https://www.tripadvisor.cn/Hotel_Review-g298556-d5864993-Reviews-Grand_Bravo_Guilin-Guilin_Guangxi.html',proxies = proxies)
    print(res.text)
