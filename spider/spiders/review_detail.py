# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy import FormRequest
from spider.items import CommentItem
import datetime

user_info_url = 'https://www.tripadvisor.com/MemberOverlay?Mode=owa&uid={uid}&c=&src={src}&fus=false&partner=false&LsoId=&metaReferer=ShowUserReviewsHotels'
detail_review_url = 'https://www.tripadvisor.com/OverlayWidgetAjax'


def parse_hotel_id(url):
    result = []
    if type(url) is list:
        for i in range(len(url)):
            result.append(re.findall('d\d+(?=-)', url[i])[0])
        return result
    return re.findall('d\d+(?=-)', url)[0]


class ReviewDetailSpider(scrapy.Spider):
    name = 'review_detail'
    allowed_domains = ['tripadvisor.com', 'tripadvisor.cn']
    start_urls = [
        'https://www.tripadvisor.cn/Hotel_Review-g297407-d1139860-Reviews-Hilton_Xiamen-Xiamen_Fujian.html']
    data = {'preferFriendReviews': 'FALSE',
            'filterSeasons': '',
            'reqNum': '1',
            'filterLang': 'zhCN',  #
            'isLastPoll': 'false',
            # 'paramSeqId': 1,
            'changeSet': 'REVIEW_LIST',
            # 'puid': 'W@q@6AoQI4UAALjdO38AAABN'
            }  # puid


    """
    //*[@data-value="zhCN"]/label/span[@class="count"]
    """
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
            print(url)
            yield scrapy.FormRequest(url, formdata=self.data, method='POST', callback=self.parse, meta={'max': 3},
                                     dont_filter=True)


    # https://www.tripadvisor.cn/Hotel_Review-g297407-d1139860-Reviews-Hilton_Xiamen-Xiamen_Fujian.html

    def parse(self, response):
        print(response.request.url)
        review = response.xpath('//*[@class="quote"]')
        hotel_id = parse_hotel_id(response.request.url)
        print("hotel_id\t", hotel_id)
        maxTimes = response.meta['max']
        while review == [] and maxTimes != 0:
            yield scrapy.FormRequest(response.request.url, method='POST', formdata=self.data, callback=self.parse,
                                     meta={'max': maxTimes - 1}, dont_filter=True)
        # 申请评论详情页

        # 对每一页的review解析出对应的review详情页面
        for quote in review:
            print(quote)

            reviewObj = re.search('/ShowUserReviews.+html', str(quote.extract()), re.M | re.I)
            id = re.search('(?<=r)\d+', reviewObj.group()).group()
            params = {'Mode': 'EXPANDED_HOTEL_REVIEWS',
                      'metaReferer': 'Restaurant_Review',
                      'reviews': id}

            yield FormRequest(detail_review_url, formdata=params, callback=self.parse_review_detail, method='GET',
                              meta={'id': id})


    def parse_review_detail(self, response):
        print(response.request.url)

        comment = CommentItem()

        comment['comment_id'] = response.meta['id']
        noquotes = response.xpath('//*/span[@class="noQuotes"]').extract()
        title = re.search('(?<=>)[\s\S]*(?=<)', str(noquotes[0]))
        reviewTitle = title.group()
        comment['title'] = reviewTitle
        print(reviewTitle)

        # 评论内容
        p = response.xpath('//*/p[@class="partial_entry"]').extract()
        body = re.search('(?<=>).*(?=<)', str(p[0]))
        reviewText = re.sub('<br>|<br/>', '', body.group())
        comment['content'] = reviewText
        print(reviewText)

        # 评论日期
        ratingDate = response.xpath('//*/span[@class="ratingDate relativeDate"]').extract()
        review_date = re.search('(?<=title=").*(?=">)', str(ratingDate[0]))
        time_format = datetime.datetime.strptime(review_date.group(), '%B %d, %Y')
        reviewDate = time_format.strftime('%Y/%m/%d')
        comment['comment_date'] = reviewDate
        print(reviewDate)

        ratingObj = re.search('(?<=span class="ui_bubble_rating bubble_)\d(?=0)', str(response.text))
        reviewRating = ratingObj.group()
        comment['rating'] = reviewRating
        print(reviewRating)

        try:
            uid_src = response.xpath("//*[@class='member_info']").extract()
            uidObj = re.search('(?<=UID_).*?(?=-SRC_)', str(uid_src[0]))
            uid = uidObj.group()
            print(uid)
            srcObj = re.search('(?<=SRC_)\d+', str(uid_src[0]))
            src = srcObj.group()
            print(src)
            #yield Request(url=user_info_url.format(uid=uid, src=src), callback=self.parse_user)

        except:
            pass

        '''
        uid_src = response.xpath("//*[@class='member_info']").extract()
        uidObj = re.search('(?<=UID_).*?(?=-SRC_)', str(uid_src[0]))
        uid = uidObj.group()
    
        srcObj = re.search('(?<=SRC_)\d+', str(uid_src[0]))
        src = srcObj.group()
        '''

    # def parse_user(self, response):
    #     print(response.request.url)
    #     contributor_text = response.text
    #     contributor_urlObj = re.search('/Profile.*(?=")', str(contributor_text))
    #     reviewerURL = 'https://www.tripadvisor.com' + contributor_urlObj.group()
    #     print("评论者链接是：", end='')
    #     print(reviewerURL)
    #     try:
    #         badgeinfo = response.xpath('//*[@class="badgeinfo"]')
    #         contributor_LevelObj = re.search('\d', str(badgeinfo[0]))
    #         contributorLevel = contributor_LevelObj.group()
    #     except:
    #         contributorLevel = None
    #     print("评论者等级：", end='')
    #     print(contributorLevel)
    #
    #     memberdescription = response.xpath('//*/ul[@class="memberdescriptionReviewEnhancements"]').extract_first()
    #     print(memberdescription)
    #     genderObj = re.search('man(?= from)|Man(?= from)|woman(?= from)|Woman(?= from)',
    #                           memberdescription)
    #     try:
    #         reviewerGender = genderObj.group().lower()
    #     except:
    #         reviewerGender = None
    #     print("评论者性别：", end='')
    #     print(reviewerGender)
    #     ageObj = re.search('\d+-\d+|\d+\+', memberdescription)
    #     try:
    #         reviewerAge = ageObj.group()
    #     except:
    #         reviewerAge = None
    #     print("评论者年龄：", end='')
    #     print(reviewerAge)
    #     try:
    #         memberTagReview = response.xpath('//*/a[@class="memberTagReviewEnhancements"]')
    #         travelerType = memberTagReview.text
    #     except:
    #         travelerType = None
    #     print("评论者类型：", end='')
    #     print(travelerType)
    #     badgeTextReviewEnhancements = response.xpath('//*/span[@class="badgeTextReviewEnhancements"]').extract()
    #     reviewerContributionNum = reviewerCityNum = reviewerPhotoNum = reviewerHelpfulVotes = None
    #     for badgetext in badgeTextReviewEnhancements:
    #         bandgetypeObj = re.search('(?<=\d\s).*(?=</span>)', badgetext)
    #         bandgetype = bandgetypeObj.group()
    #         if bandgetype == 'Contributions' or bandgetype == 'Contribution':
    #             contributionsObj = re.search('\d+', str(badgetext))
    #             reviewerContributionNum = contributionsObj.group()
    #         elif bandgetype == 'Cities visited' or bandgetype == 'City visited':
    #             contributor_cities_visitedObj = re.search('\d+', str(badgetext))
    #             reviewerCityNum = contributor_cities_visitedObj.group()
    #         elif bandgetype == 'Helpful votes' or bandgetype == 'Helpful vote':
    #             contributor_helpful_votesObj = re.search('\d+', str(badgetext))
    #             reviewerHelpfulVotes = contributor_helpful_votesObj.group()
    #         elif bandgetype == 'Photos' or bandgetype == 'Photo':
    #             contributor_photosObj = re.search('\d+', str(badgetext))
    #             reviewerPhotoNum = contributor_photosObj.group()
    #     print('评论者评论总数，访问城市数目，发表照片数目，获得有用投票总数：', end='')
    #     print(reviewerContributionNum, reviewerCityNum, reviewerHelpfulVotes, reviewerPhotoNum)
    #     chartRowReviewEnhancements = response.xpath('//*[@class="chartRowReviewEnhancements"]').extract()
    #     reviewerExcellentRating = reviewerVeryGoodRating = reviewerAverageRating = reviewerPoorRating = reviewerTerribleRating = None
    #     for chartRow in chartRowReviewEnhancements:
    #         chartRowObj = re.search('(?<=>).*(?=</span>)', chartRow)
    #         chartRowtype = chartRowObj.group()
    #         if chartRowtype == 'Excellent':
    #             contributor_review_excellentObj = re.search('\d+(?=</span>)', str(chartRow))
    #             reviewerExcellentRating = contributor_review_excellentObj.group()
    #         elif chartRowtype == 'Very good':
    #             contributor_review_goodObj = re.search('\d+(?=</span>)', str(chartRow))
    #             reviewerVeryGoodRating = contributor_review_goodObj.group()
    #         elif chartRowtype == 'Average':
    #             contributor_review_averageObj = re.search('\d+(?=</span>)', str(chartRow))
    #             reviewerAverageRating = contributor_review_averageObj.group()
    #         elif chartRowtype == 'Poor':
    #             contributor_review_poorObj = re.search('\d+(?=</span>)', str(chartRow))
    #             reviewerPoorRating = contributor_review_poorObj.group()
    #         elif chartRowtype == 'Terrible':
    #             contributor_review_terribleObj = re.search('\d+(?=</span>)', str(chartRow))
    #             reviewerTerribleRating = contributor_review_terribleObj.group()
    #     print("各星评论数目：", end='')
    #     print(reviewerExcellentRating, reviewerVeryGoodRating, reviewerAverageRating,
    #           reviewerPoorRating,
    #           reviewerTerribleRating)


# if __name__ == '__main__':
#     url = 'https://www.tripadvisor.cn/Hotel_Review-g298556-d10466401-Reviews-or15-Ease_Hostel-Guilin_Guangxi.html'
#     data = {'preferFriendReviews': 'FALSE',
#             'filterSeasons': '',
#             'filterLang': 'zhCN',  #
#             'reqNum': 1,
#             'isLastPoll': 'false',
#             # 'paramSeqId': 1,
#             'changeSet': 'REVIEW_LIST',
#             # 'puid': 'W@q@6AoQI4UAALjdO38AAABN'
#             }  # puid
#     headers = {
#         # 'referer': 'https://www.tripadvisor.com/Hotel_Review-g60491-d101222-Reviews-Super_8_by_Wyndham_Jackson_Hole-Jackson_Jackson_Hole_Wyoming.html',
#         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
#         'x-requested-with': 'XMLHttpRequest'}
#     req = requests.post(url, data=data, headers=headers)
#     print(req.status_code)
#     data = req.content
#     print(data)
