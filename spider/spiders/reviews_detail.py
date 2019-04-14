# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import re
from spider.items import CommentItem
import datetime


class ReviewsDetailSpider(scrapy.Spider):
    name = 'reviews_detail'
    allowed_domains = ['tripadvisor.com']
    base_url = 'https://www.tripadvisor.com/OverlayWidgetAjax'
    start_urls = [
        'https://www.tripadvisor.com/ShowUserReviews-g294212-d3198755-r647670742-Beijing_161_Hotel_Hulu_Courtyard-Beijing.html']

    user_info_url = 'https://www.tripadvisor.com/MemberOverlay?Mode=owa&uid={uid}&c=&src={src}&fus=false&partner=false&LsoId=&metaReferer=ShowUserReviewsHotels'

    def start_requests(self):
        for url in self.start_urls:
            idObj = re.search('(?<=r)\d+', url)
            id = str(idObj.group())
            params = {'Mode': 'EXPANDED_HOTEL_REVIEWS',
                      'metaReferer': 'Restaurant_Review',
                      'reviews': id}

            yield FormRequest(self.base_url, formdata=params, callback=self.parse, method='GET', meta={'id': id})

    def parse(self, response):

        comment = CommentItem()
        comment['comment_id'] = response.meta['id']
        noquotes = response.xpath('//*/span[@class="noQuotes"]').extract()
        title = re.search('(?<=>)[\s\S]*(?=<)', str(noquotes[0]))
        reviewTitle = title.group()
        print('评论题目是：', end='')
        print(reviewTitle)
        comment['title'] = reviewTitle

        # 评论内容
        p = response.xpath('//*/p[@class="partial_entry"]').extract()
        body = re.search('(?<=>).*(?=<)', str(p[0]))
        reviewText = re.sub('<br>|<br/>', '', body.group())
        print('评论内容是：', end='')
        print(reviewText)
        comment['content'] = reviewText

        # 评论日期
        ratingDate = response.xpath('//*/span[@class="ratingDate relativeDate"]').extract()
        review_date = re.search('(?<=title=").*(?=">)', str(ratingDate[0]))
        time_format = datetime.datetime.strptime(review_date.group(), '%B %d, %Y')
        reviewDate = time_format.strftime('%Y/%m/%d')
        print('评论日期：', end='')
        print(reviewDate)
        comment['comment_date'] = reviewDate

        ratingObj = re.search('(?<=span class="ui_bubble_rating bubble_)\d(?=0)', str(response.text))
        reviewRating = ratingObj.group()
        print('评论等级：', end='')
        print(reviewRating)
        comment['rating'] = reviewRating

        uid_src = response.xpath("//*[@class='member_info']").extract()
        uidObj = re.search('(?<=UID_).*?(?=-SRC_)', str(uid_src[0]))
        uid = uidObj.group()
        print(uid)
        srcObj = re.search('(?<=SRC_)\d+', str(uid_src[0]))
        src = srcObj.group()
        print(src)
        yield Request(url=self.user_info_url.format(uid=uid, src=src), callback=self.parse_user)

    def parse_user(self, response):
        print(response.request.url)
        contributor_text = response.text
        contributor_urlObj = re.search('/Profile.*(?=")', str(contributor_text))
        reviewerURL = 'https://www.tripadvisor.com' + contributor_urlObj.group()
        print("评论者链接是：", end='')
        print(reviewerURL)
        try:
            badgeinfo = response.xpath('//*[@class="badgeinfo"]')
            contributor_LevelObj = re.search('\d', str(badgeinfo[0]))
            contributorLevel = contributor_LevelObj.group()
        except:
            contributorLevel = None
        print("评论者等级：", end='')
        print(contributorLevel)

        memberdescription = response.xpath('//*/ul[@class="memberdescriptionReviewEnhancements"]').extract_first()
        print(memberdescription)
        genderObj = re.search('man(?= from)|Man(?= from)|woman(?= from)|Woman(?= from)',
                              memberdescription)
        try:
            reviewerGender = genderObj.group().lower()
        except:
            reviewerGender = None
        print("评论者性别：", end='')
        print(reviewerGender)
        ageObj = re.search('\d+-\d+|\d+\+', memberdescription)
        try:
            reviewerAge = ageObj.group()
        except:
            reviewerAge = None
        print("评论者年龄：", end='')
        print(reviewerAge)
        try:
            memberTagReview = response.xpath('//*/a[@class="memberTagReviewEnhancements"]')
            travelerType = memberTagReview.text
        except:
            travelerType = None
        print("评论者类型：", end='')
        print(travelerType)
        badgeTextReviewEnhancements = response.xpath('//*/span[@class="badgeTextReviewEnhancements"]').extract()
        reviewerContributionNum = reviewerCityNum = reviewerPhotoNum = reviewerHelpfulVotes = None
        for badgetext in badgeTextReviewEnhancements:
            bandgetypeObj = re.search('(?<=\d\s).*(?=</span>)', badgetext)
            bandgetype = bandgetypeObj.group()
            if bandgetype == 'Contributions' or bandgetype == 'Contribution':
                contributionsObj = re.search('\d+', str(badgetext))
                reviewerContributionNum = contributionsObj.group()
            elif bandgetype == 'Cities visited' or bandgetype == 'City visited':
                contributor_cities_visitedObj = re.search('\d+', str(badgetext))
                reviewerCityNum = contributor_cities_visitedObj.group()
            elif bandgetype == 'Helpful votes' or bandgetype == 'Helpful vote':
                contributor_helpful_votesObj = re.search('\d+', str(badgetext))
                reviewerHelpfulVotes = contributor_helpful_votesObj.group()
            elif bandgetype == 'Photos' or bandgetype == 'Photo':
                contributor_photosObj = re.search('\d+', str(badgetext))
                reviewerPhotoNum = contributor_photosObj.group()
        print('评论者评论总数，访问城市数目，发表照片数目，获得有用投票总数：', end='')
        print(reviewerContributionNum, reviewerCityNum, reviewerHelpfulVotes, reviewerPhotoNum)
        chartRowReviewEnhancements = response.xpath('//*[@class="chartRowReviewEnhancements"]').extract()
        reviewerExcellentRating = reviewerVeryGoodRating = reviewerAverageRating = reviewerPoorRating = reviewerTerribleRating = None
        for chartRow in chartRowReviewEnhancements:
            chartRowObj = re.search('(?<=>).*(?=</span>)', chartRow)
            chartRowtype = chartRowObj.group()
            if chartRowtype == 'Excellent':
                contributor_review_excellentObj = re.search('\d+(?=</span>)', str(chartRow))
                reviewerExcellentRating = contributor_review_excellentObj.group()
            elif chartRowtype == 'Very good':
                contributor_review_goodObj = re.search('\d+(?=</span>)', str(chartRow))
                reviewerVeryGoodRating = contributor_review_goodObj.group()
            elif chartRowtype == 'Average':
                contributor_review_averageObj = re.search('\d+(?=</span>)', str(chartRow))
                reviewerAverageRating = contributor_review_averageObj.group()
            elif chartRowtype == 'Poor':
                contributor_review_poorObj = re.search('\d+(?=</span>)', str(chartRow))
                reviewerPoorRating = contributor_review_poorObj.group()
            elif chartRowtype == 'Terrible':
                contributor_review_terribleObj = re.search('\d+(?=</span>)', str(chartRow))
                reviewerTerribleRating = contributor_review_terribleObj.group()
        print("各星评论数目：", end='')
        print(reviewerExcellentRating, reviewerVeryGoodRating, reviewerAverageRating,
              reviewerPoorRating,
              reviewerTerribleRating)
