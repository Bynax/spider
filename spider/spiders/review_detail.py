# -*- coding: utf-8 -*-
import scrapy
import re
import requests
from spider.items import CommentItem


class ReviewDetailSpider(scrapy.Spider):
    name = 'review_detail'
    allowed_domains = ['tripadvisor.com']
    start_urls = [
        'https://www.tripadvisor.cn/Hotel_Review-g294212-d793789-Reviews-or10-Hotel_Kapok_Beijing-Beijing.html',
        'https://www.tripadvisor.cn/Hotel_Review-g294212-d793789-Reviews-or15-Hotel_Kapok_Beijing-Beijing.html']
    data = {'preferFriendReviews': 'FALSE',
            'filterSeasons': '',
            # 'filterLang': 'zhCN',  #
            'reqNum': '1',
            'filterLang': 'ALL',  #
            'isLastPoll': 'false',
            # 'paramSeqId': 1,
            'changeSet': 'REVIEW_LIST',
            # 'puid': 'W@q@6AoQI4UAALjdO38AAABN'
            }  # puid

    '''
    reqNum: 1
isLastPoll: false
paramSeqId: 0
waitTime: 24
changeSet: REVIEW_LIST
puid: XLKm58CoATAAAD6kMG8AAAHX
    '''

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.FormRequest(url, formdata=self.data, method='POST', callback=self.parse, meta={'max': 3},
                                     dont_filter=True)

    def parse(self, response):
        print(response.request.url)
        review = response.xpath('//*[@class="quote"]')
        maxTimes = response.meta['max']
        while review == [] and maxTimes != 0:
            yield scrapy.FormRequest(response.request.url, method='POST', formdata=self.data, callback=self.parse,
                                     meta={'max': maxTimes - 1}, dont_filter=True)
        # 申请评论详情页

        base_url = 'https://www.tripadvisor.com/OverlayWidgetAjax'
        for quote in review:
            print(quote)
            reviewObj = re.search('/ShowUserReviews.+html', str(quote.extract()), re.M | re.I)
            review_url = 'https://www.tripadvisor.com' + reviewObj.group()
            params = {'Mode': 'EXPANDED_HOTEL_REVIEWS',
                      'metaReferer': 'Restaurant_Review',
                      'reviews': id}

            yield scrapy.FormRequest(base_url, params=params, callback=self.parse_review_detail,
                                     dont_filter=True)

    def parse_review_detail(self, response):
        # 评论的id
        comment = CommentItem()
        comment_id = re.search('(?<=r)\d+', response.request.url).group()
        print(comment_id)
        comment['comment_id'] = comment_id

        # 评论标题
        noquotes = response.xpath('//*/span[@class="noQuotes"]')
        title = re.search('(?<=>)[\s\S]*(?=<)', str(noquotes[0]))
        reviewTitle = title.group()
        print('评论题目是：', end='')
        print(reviewTitle)


if __name__ == '__main__':
    base_url = 'https://www.tripadvisor.com/OverlayWidgetAjax'
    params = {'Mode': 'EXPANDED_HOTEL_REVIEWS',
              'metaReferer': 'Restaurant_Review',
              'reviews': '588647734'}
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'}
    req = requests.get(base_url, params=params, headers=headers)
    data = req.text
    print(data)
