# -*- coding: utf-8 -*-
from scrapy import Request, Spider, FormRequest
import re
import math
from spider.items import HotelItem, NeighborHotel, CommentItem, PersonItem
import os, datetime
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError

pre_url = 'https://www.tripadvisor.cn'
user_info_url = 'https://www.tripadvisor.com/MemberOverlay?Mode=owa&uid={uid}&c=&src={src}&fus=false&partner=false&LsoId=&metaReferer=ShowUserReviewsHotels'
detail_review_url = 'https://www.tripadvisor.com/OverlayWidgetAjax'

review_data = {'preferFriendReviews': 'FALSE',
               'filterSeasons': '',
               'filterLang': 'ALL',  #
               'reqNum': '1',
               'isLastPoll': 'false',
               # 'paramSeqId': 1,
               'changeSet': 'REVIEW_LIST',
               # 'puid': 'W@q@6AoQI4UAALjdO38AAABN'
               }  # puid


# 后续处理可以设置宾馆的id，查看是否已爬取，设置断点继续

def parse_city_id(url):
    return re.findall('g\d+(?=-)', url)[0]


def parse_hotel_id(url):
    result = []
    if type(url) is list:
        for i in range(len(url)):
            result.append(re.findall('d\d+(?=-)', url[i])[0])
        return result
    return re.findall('d\d+(?=-)', url)[0]


class TripadvSpider(Spider):
    name = 'hotel_detail'  # 爬虫名
    allowed_domains = ['tripadvisor.com', 'tripadvisor.cn']
    file_names = []

    def __init__(self):
        abs_cwd = os.path.join(os.path.abspath(os.getcwd()), 'hotel_links')
        for filename in os.listdir(abs_cwd):
            self.file_names.append(os.path.join(abs_cwd, filename))

    def start_requests(self):
        for filename in self.file_names:
            with open(filename, 'r+', encoding='utf-8')as f:
                lines = f.readlines()
                for line in lines:
                    hotel_detail_url = line
                    yield Request((pre_url + hotel_detail_url).rstrip('%0A').strip(), callback=self.parse_detail_hotel,
                                  meta={'max': 3},errback=self.errback)

    def parse_neighbor_initial(self, response):
        xpath_neibor_nums = '//*[@id="taplc_main_pagination_bar_dusty_hotels_resp_0"]/div/div/div/div/a/text()'  # 页数列表，最后一项为页数
        neighbor_nums = response.xpath(xpath_neibor_nums).extract()[-1]
        links = response.xpath('//*[@class="listing_title"]/a/@href').extract()
        distance = response.xpath('//*[@class="distance linespace is-shown-at-mobile"]/div/b/text()').extract()
        hotel_id = parse_hotel_id(links)
        target_id = parse_hotel_id(response.request.url)
        len1 = len(hotel_id)
        len2 = len(distance)
        item_num = min(len1, len2)
        for i in range(item_num):
            neighbor = NeighborHotel()
            neighbor['hotel_id'] = hotel_id[i]
            neighbor['target_id'] = target_id
            neighbor['distance'] = distance[i]
            yield neighbor

        url_start = re.search('.+\d+', response.request.url, re.M | re.I)
        page_num = min(int(neighbor_nums), 5)
        for i in range(page_num):
            page_url = re.sub('.+\d+', url_start.group() + '-oa' + str(i * 30), response.request.url)
            yield Request(page_url, callback=self.parse_neighbor, meta={'max': 3},errback=self.errback)

    def parse_neighbor(self, response):
        links = response.xpath('//*[@class="listing_title"]/a/@href').extract()
        distance = response.xpath('//*[@class="distance linespace is-shown-at-mobile"]/div/b/text()').extract()
        hotel_id = parse_hotel_id(links)
        target_id = parse_hotel_id(response.request.url)
        len1 = len(hotel_id)
        len2 = len(distance)
        item_num = min(len1, len2)
        for i in range(item_num):
            neighbor = NeighborHotel()
            neighbor['hotel_id'] = hotel_id[i]
            neighbor['target_id'] = target_id
            neighbor['distance'] = distance[i]
            yield neighbor

    def parse_detail_hotel(self, response):
        hotel = HotelItem()
        xpath_review_count = '//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/a/span/text()'  # 评论数量
        xpath_hotel_name = '//*[@id="HEADING"]'  #
        xpath_youhui = '//*[@id="taplc_resp_hr_atf_meta_0"]/div/div/div'  # 优惠
        xpath_rank = '//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span'  # 酒店排名
        xpath_grade = '//*[@id="OVERVIEW"]/div[2]/div[1]/div/span[1]/text()'  # 酒店分数 1-5
        xpath_address = '//*/span[@class="street-address"]/text()'  # 地址
        xpath_pics_num = '//*[@id="component_12"]/div/div[1]/div/div[1]/div/div[5]/div/div/span[3]/text()'  # 照片张数,两个括号一个数字
        xpath_feature = '//*[@id="ABOUT_TAB"]/div[2]/div[2]/div/div/div[2]/div[2]/div/div/text()'  # 酒店特色
        xpath_star = '//*[@id="OVERVIEW"]/div[2]/div[4]/div[2]/div/div[2]/div[3]/div/text()'  # 酒店星级
        xpath_rooms = '//*[@id="ABOUT_TAB"]/div[2]/div[3]/div[2]/div[3]/div[2]/div/text()'  # 房间数
        xpath_room_type = '//*[@id="ABOUT_TAB"]/div[2]/div[3]/div[2]/div[1]/div[6]/div/text()'  # 客房类型
        xpath_award = '//*[@class="sub_content badges is-shown-at-desktop"]'  # 奖项
        xpath_neighbor = '//*[@id="taplc_resp_hr_nearby_0"]/div/div[3]/div[1]/a/@href'  # 附近酒店链接

        # 照片数量
        pics_num = response.xpath(xpath_pics_num).extract()
        if pics_num is None:
            pic_num = 'N/A'
        else:
            pic_num = ''.join(pics_num)
        hotel['pics_num'] = pic_num if pic_num is not None else 'N/A'

        # 点评数量
        review = response.xpath(xpath_review_count)
        if review is None:
            review_count = 'N/A'
        else:
            try:
                textObj = re.sub(',', '', review.extract_first())
                text = re.search('\d+', textObj)
                review_count = text.group()
            except:
                review_count = 'N/A'
        hotel['comment_num'] = review_count if review_count is not None else 'N/A'

        # 找出评论页面
        try:
            int(review_count)
            url_start = re.search('.+Reviews', response.request.url)
            review_page_urls = []
            review_page_urls.append(response.request.url)
            page_nums = min((math.ceil(math.ceil(int(review_count) / 5)), 10))
            for n in range(1, page_nums):
                review_page_url = re.sub('.+Reviews', url_start.group() + '-or' + str(n * 5), response.request.url)
                review_page_urls.append(review_page_url)
                headers = {
                    "X-Requested-With": "XMLHttpRequest",

                }
                yield FormRequest(review_page_url, formdata=review_data, method="post", callback=self.parse_review,
                                  meta={'max': 3}, headers=headers,errback=self.errback)
        except:
            pass

        # 排名
        try:
            rank = response.xpath(xpath_rank)
            rank_b = "".join(re.findall('\d+', rank.xpath('.//b/text()').extract_first()))
        except:
            rank_b = 'N/A'
        hotel['rank'] = rank_b if rank_b is not None else 'N/A'
        # print(rank_b)

        # 酒店中英文名称
        try:
            hotel_name = response.xpath(xpath_hotel_name)
            cn_name = hotel_name.xpath('.//text()').extract_first()
            en_name = hotel_name.xpath('.//div/text()').extract_first()
        except:
            cn_name = 'N/A'
            en_name = 'N/A'

        hotel['hotel_name_cn'] = cn_name if cn_name is not None else 'N/A'
        hotel['hotel_name_en'] = en_name if en_name is not None else 'N/A'

        # 酒店评分得分
        try:
            hotel_grade = response.xpath(xpath_grade).extract_first()
        except:
            hotel_grade = 'N/A'
        hotel['grade'] = hotel_grade if hotel_grade is not None else 'N/A'

        # 具体地址
        try:
            hotel_address = response.xpath(xpath_address).extract_first()
        except:
            hotel_address = 'N/A'
        hotel['address'] = hotel_address if hotel_address is not None else 'N/A'

        # 奖项与认证
        badgesObj = response.xpath(xpath_award).extract()
        badges = re.findall('(?<=<span class="ui_icon ).*?(?=</span>)', str(badgesObj))
        for badge in badges:
            badges[badges.index(badge)] = re.sub('.*>', '', badge)
        a = ', '
        hotelAwards = a.join(badges)
        try:
            if badgesObj.xpath('../span[@class="award_text"]') != None:
                s = badgesObj.find('span', class_='award_text')
                hotelAwards = s.text + hotelAwards
        except:
            hotelAwards = 'N/a'
        hotel['award'] = hotelAwards if hotelAwards is not None else 'N/A'

        # 宾馆特色
        try:
            styleObj = response.xpath('//*[@class="textitem style"]/text()').extract()
            hotelStyle = ",".join(styleObj)
        except:
            hotelStyle = 'N/A'

        hotel['style'] = hotelStyle if hotelStyle is not None else 'N/A'

        # 酒店特色
        try:
            # 不带有酒店说明的xpath
            feature = response.xpath(xpath_feature).extract()
            # 带有酒店说明的xpath
            feature_with_instr = response.xpath(
                '//*[@id="ABOUT_TAB"]/div[2]/div[3]/div/div/div[2]/div[2]/div/div/text()').extract()
            hotel_feature = ",".join(feature + feature_with_instr)

        except:
            hotel_feature = 'N/A'
        hotel['feature'] = hotel_feature if hotel_feature is not None else 'N/A'

        # 客房类型
        try:
            # 不带说明
            r_type = response.xpath(xpath_room_type).extract()

            # 带说明
            r_type_instr = response.xpath(
                '//*[@id="ABOUT_TAB"]/div[2]/div[4]/div[2]/div[1]/div[4]/div/text()').extract()

            room_type = ",".join(r_type + r_type_instr)

        except:
            room_type = 'N/A'

        hotel['room_type'] = room_type if room_type is not None else 'N/A'

        # 酒店星级
        try:
            star = "".join(re.findall('\d+', response.xpath(xpath_star).extract_first()))
        except:
            star = 'N/A'
        hotel['star'] = star if star is not None else 'N/A'

        # 房间数量
        try:
            # 不带说明
            rooms = response.xpath(xpath_rooms).extract()
            # 带说明
            rooms_instr = response.xpath('//*[@id="ABOUT_TAB"]/div[2]/div[4]/div[2]/div[3]/div[2]/div/text()').extract()
            rooms = "".join(rooms + rooms_instr)
            int(rooms)
        except:
            rooms = 'N/A'
        hotel['rooms'] = rooms if rooms is not None else 'N/A'

        # 优惠价钱
        prices = []
        try:
            yh = response.xpath(xpath_youhui)
            if yh.xpath('.//div') is not None:
                name = yh.xpath('.//div/div[1]/span/img/@alt').extract()
                price = yh.xpath('.//div/div[2]/div/div/text()').extract()
                for i in range(min(len(name), len(price))):
                    prices.append("{}:{}".format(name[i], price[i]))
            if yh.xpath('.//div[4]') is not None:
                name = yh.xpath('.//div[4]/div[1]/div[1]/div/div/span[1]/text()').extract()
                price = yh.xpath('.//div[4]/div[1]/div[1]/div/div/span[2]/text()').extract()
                for i in range(min(len(name), len(price))):
                    prices.append("{}:{}".format(name[i], price[i]))
        except:
            prices = 'N/A'

        youhui = ",".join(prices)
        hotel['youhui'] = youhui if youhui is not None else 'N/A'
        hotel['hotel_city'] = parse_city_id(response.request.url)
        hotel['hotel_id'] = parse_hotel_id(response.request.url)
        yield hotel

        try:
            neighbor = response.xpath(xpath_neighbor).extract()[-1]
            neighbor_url = "{}{}".format(pre_url, neighbor)
            # 字符串
            yield Request(neighbor_url,errback=self.errback, callback=self.parse_neighbor_initial, meta={'max': 3})
        except:
            pass

    def parse_review(self, response):
        review = response.xpath('//*[@class="quote"]')
        hotel_id = parse_hotel_id(response.request.url)

        # 申请评论详情页

        # 对每一页的review解析出对应的review详情页面
        for quote in review:
            reviewObj = re.search('/ShowUserReviews.+html', str(quote.extract()), re.M | re.I)
            id = re.search('(?<=r)\d+', reviewObj.group()).group()
            params = {'Mode': 'EXPANDED_HOTEL_REVIEWS',
                      'metaReferer': 'Restaurant_Review',
                      'reviews': id}

            yield FormRequest(detail_review_url,errback=self.errback, formdata=params, callback=self.parse_review_detail, method='GET',
                              meta={'id': id, 'max': 3, 'hotel_id': hotel_id})

    def parse_review_detail(self, response):
        try:
            comment = CommentItem()

            # 评论id
            comment['comment_id'] = response.meta['id']
            noquotes = response.xpath('//*/span[@class="noQuotes"]').extract()
            title = re.search('(?<=>)[\s\S]*(?=<)', str(noquotes[0]))
            reviewTitle = title.group()
            comment['title'] = reviewTitle

            # 对用酒店id
            comment['hotel_id'] = response.meta['hotel_id']

            # 评论内容
            p = response.xpath('//*/p[@class="partial_entry"]').extract()
            body = re.search('(?<=>).*(?=<)', str(p[0]))
            reviewText = re.sub('<br>|<br/>', '', body.group())
            comment['content'] = reviewText if len(reviewText) < 1024 else reviewText[0:1024]

            # 评论日期
            ratingDate = response.xpath('//*/span[@class="ratingDate relativeDate"]').extract()
            review_date = re.search('(?<=title=").*(?=">)', str(ratingDate[0]))
            time_format = datetime.datetime.strptime(review_date.group(), '%B %d, %Y')
            reviewDate = time_format.strftime('%Y/%m/%d')
            comment['comment_date'] = reviewDate

            ratingObj = re.search('(?<=span class="ui_bubble_rating bubble_)\d(?=0)', str(response.text))
            reviewRating = ratingObj.group()
            comment['rating'] = reviewRating

            uid_src = response.xpath("//*[@class='member_info']").extract()
            uidObj = re.search('(?<=UID_).*?(?=-SRC_)', str(uid_src[0]))
            uid = uidObj.group()

            srcObj = re.search('(?<=SRC_)\d+', str(uid_src[0]))
            src = srcObj.group()

            # 评论人id
            comment['person'] = uid
            yield comment
            if uid is not None:
                yield Request(url=user_info_url.format(uid=uid, src=src),errback=self.errback, callback=self.parse_user,
                              meta={'max': 3, 'uid': uid})
        except:
            pass

    def parse_user(self, response):
        person = PersonItem()
        # print(response.request.url)
        # contributor_text = response.text
        # contributor_urlObj = re.search('/Profile.*(?=")', str(contributor_text))
        # reviewerURL = 'https://www.tripadvisor.com' + contributor_urlObj.group()
        # print("评论者链接是：", end='')
        # print(reviewerURL)

        person['person_id'] = response.meta['uid']

        # 等级
        try:
            badgeinfo = response.xpath('//*[@class="badgeinfo"]')
            contributor_LevelObj = re.search('\d', str(badgeinfo[0]))
            contributorLevel = contributor_LevelObj.group()
        except:
            contributorLevel = 'N/A'

        person['grade'] = contributorLevel
        # print("评论者等级：", end='')

        # print(contributorLevel)

        memberdescription = response.xpath('//*/ul[@class="memberdescriptionReviewEnhancements"]')
        # 描述
        try:
            # print("hello:{}".format(",".join(memberdescription.xpath(".//li/text()").extract())))
            person['description'] = ",".join(memberdescription.xpath(".//li/text()").extract())
        except:
            person['description'] = 'N/A'

        # 性别
        genderObj = re.search('man(?= from)|Man(?= from)|woman(?= from)|Woman(?= from)',
                              memberdescription.extract_first())
        try:
            reviewerGender = genderObj.group().lower()
        except:
            reviewerGender = 'N/A'
        person['gender'] = reviewerGender
        # print("评论者性别：", end='')
        # print(reviewerGender)

        # 年龄
        ageObj = re.search('\d+-\d+|\d+\+', memberdescription.extract_first())
        try:
            reviewerAge = ageObj.group()
        except:
            reviewerAge = 'N/A'

        person['age'] = reviewerAge
        # print("评论者年龄：", end='')
        # print(reviewerAge)

        # 类型
        try:
            memberTagReview = response.xpath('//*/a[@class="memberTagReviewEnhancements"]')
            travelerType = memberTagReview.text
        except:
            travelerType = 'N/A'

        person['member_type'] = travelerType
        # print("评论者类型：", end='')
        # print(travelerType)

        # 勋章
        badgeTextReviewEnhancements = response.xpath('//*/span[@class="badgeTextReviewEnhancements"]').extract()
        reviewerContributionNum = reviewerCityNum = reviewerHelpfulVotes = None
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

        person['review_total_num'] = 'N/A' if reviewerContributionNum is None else str(reviewerContributionNum)
        person['visited_city_num'] = 'N/A' if reviewerCityNum is None else str(reviewerCityNum)
        person['photo_nums'] = 'N/A' if reviewerCityNum is None else str(reviewerCityNum)
        person['userfule_votes'] = 'N/A' if reviewerHelpfulVotes is None else str(reviewerHelpfulVotes)

        # 评论
        chartRowReviewEnhancements = response.xpath('//*[@class="chartRowReviewEnhancements"]').extract()
        reviewerExcellentRating = reviewerVeryGoodRating = reviewerAverageRating = reviewerPoorRating = reviewerTerribleRating = 'N/A'
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
        person['review_dis'] = "{},{},{},{},{}".format(reviewerExcellentRating, reviewerVeryGoodRating,
                                                       reviewerAverageRating, reviewerPoorRating,
                                                       reviewerTerribleRating)
        yield person

    # errorback方法
    def errback(self, failure):
        # log all errback failures,
        # in case you want to do something special for some errors,
        # you may need the failure's type
        self.logger.error(repr(failure))

        # if isinstance(failure.value, HttpError):
        if failure.check(HttpError):
            # you can get the response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        # elif isinstance(failure.value, DNSLookupError):
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        # elif isinstance(failure.value, TimeoutError):
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

# if __name__ == '__main__':
#     review_data = {'preferFriendReviews': 'FALSE',
#                    'filterSeasons': '',
#                    'filterLang': 'ALL',  #
#                    'reqNum': '1',
#                    'isLastPoll': 'false',
#                    # 'paramSeqId': 1,
#                    'changeSet': 'REVIEW_LIST',
#                    # 'puid': 'W@q@6AoQI4UAALjdO38AAABN'
#                    }  # puid
#     url = 'https://www.tripadvisor.cn/Hotel_Review-g298556-d10466401-Reviews-or15-Ease_Hostel-Guilin_Guangxi.html'
#     url2 = 'https://www.tripadvisor.cn/Hotel_Review-g294212-d1916310-Reviews-or5-Days_Hotel_Beijing_New_Exhibition_Center-Beijing.html'
#     url3 = 'https://www.tripadvisor.cn/Hotel_Review-g298556-d1960177-Reviews-Guilin_Ming_Palace_International_Youth_Hostel-Guilin_Guangxi.html'
#     headers = {
#                   "X-Requested-With": "XMLHttpRequest",
#                   "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
#     }
#     res = requests.get(url3, headers=headers)
#     print(res.text)
#     print(res.status_code)
