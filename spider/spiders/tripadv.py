# -*- coding: utf-8 -*-
from scrapy import Request, Spider
import re
import math
from spider.items import HotelItem

pre_url = 'https://www.tripadvisor.cn'


# 后续处理可以设置宾馆的id，查看是否已爬取，设置断点继续
# 宾馆code提取的正则表达式为：code = re.findall('d\d+(?=-)', hotel_url)

class TripadvSpider(Spider):
    name = 'hotel_detail'  # 爬虫名
    allowed_domains = ['tripadvisor.cn']  # 允许爬取的范围

    def start_requests(self):
        hotel_detail_url = "/Hotel_Review-g294212-d1916310-Reviews-Days_Hotel_Beijing_New_Exhibition_Center-Beijing.html"
        yield Request(pre_url + hotel_detail_url, callback=self.parse_detail_hotel)

    def parse_detail_hotel(self, response):
        hotel = HotelItem()
        xpath_review_count = '//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/a/span/text()'  # 评论数量
        xpath_hotel_name = '//*[@id="HEADING"]'  #
        xpath_youhui = '//*[@id="taplc_resp_hr_atf_meta_0"]/div/div/div'  # 优惠
        # /div[4]/div[1]/div[1]/div/div/span[1]
        xpath_rank = '//*[@id="taplc_resp_hr_atf_hotel_info_0"]/div/div[1]/div/div/span'  # 酒店排名
        xpath_grade = '//*[@id="OVERVIEW"]/div[2]/div[1]/div/span[1]/text()'  # 酒店分数 1-5
        xpath_address = '//*/span[@class="street-address"]/text()'  # 地址
        xpath_pics_num = '//*[@id="component_12"]/div/div[1]/div/div[1]/div/div[5]/div/div/span[3]/text()'  # 照片张数,两个括号一个数字
        xpath_feature = '//*[@id="ABOUT_TAB"]/div[2]/div[2]/div/div/div[2]/div[2]/div/div/text()'  # 酒店特色
        xpath_star = '//*[@id="OVERVIEW"]/div[2]/div[4]/div[2]/div/div[2]/div[3]/div/text()'  # 酒店星级
        xpath_rooms = '//*[@id="ABOUT_TAB"]/div[2]/div[3]/div[2]/div[3]/div[2]/div/text()'  # 房间数
        xpath_room_type = '//*[@id="ABOUT_TAB"]/div[2]/div[3]/div[2]/div[1]/div[6]/div/text()'  # 客房类型
        xpath_award = '//*[@class="sub_content badges is-shown-at-desktop"]'  # 奖项

        # 照片数量

        pics_num = response.xpath(xpath_pics_num).extract()
        if pics_num is None:
            pic_num = 0
        else:
            pic_num = ''.join(pics_num)
        hotel['pics_num'] = pic_num
        print(pic_num)

        # 点评数量
        review = response.xpath(xpath_review_count)
        if review is None:
            review_count = 0
        else:
            textObj = re.sub(',', '', review.extract_first())
            text = re.search('\d+', textObj)
            review_count = int(text.group())
        hotel['comment_num'] = review_count
        print(review_count)

        # 找出评论页面
        url_start = re.search('.+Reviews', response.request.url)
        review_page_urls = []
        review_page_urls.append(response.request.url)
        for n in range(1, math.ceil(review_count / 5)):
            review_page_url = re.sub('.+Reviews', url_start.group() + '-or' + str(n * 5), response.request.url)
            review_page_urls.append(review_page_url)
        hotel['review_addresses'] = review_page_urls

        print(review_page_urls)

        # 排名
        try:
            rank = response.xpath(xpath_rank)
            rank_b = "".join(re.findall('\d+', rank.xpath('.//b/text()').extract_first()))
        except:
            rank_b = -1
        hotel['rank'] = rank_b
        print(rank_b)

        # 酒店中英文名称
        try:
            hotel_name = response.xpath(xpath_hotel_name)
            cn_name = hotel_name.xpath('.//text()').extract_first()
            en_name = hotel_name.xpath('.//div/text()').extract_first()
        except:
            cn_name = None
            en_name = None

        hotel['hotel_name_cn'] = cn_name
        hotel['hotel_name_en'] = en_name
        print(cn_name, en_name)

        # 酒店评分得分
        hotel_grade = response.xpath(xpath_grade).extract_first()
        hotel['grade'] = hotel_grade
        print(hotel_grade)

        # 具体地址
        try:
            hotel_address = response.xpath(xpath_address).extract_first()
        except:
            hotel_address = None
        hotel['address'] = hotel_address
        print(hotel_address)

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
            pass
        hotel['award'] = hotelAwards
        print(hotelAwards)

        # 宾馆特色
        try:
            styleObj = response.xpath('//*[@class="textitem style"]/text()').extract()
            hotelStyle = ",".join(styleObj)
        except:
            hotelStyle = None

        hotel['style'] = hotelStyle
        print(hotelStyle)

        # 酒店特色
        try:
            # 不带有酒店说明的xpath
            feature = response.xpath(xpath_feature).extract()
            # 带有酒店说明的xpath
            feature_with_instr = response.xpath(
                '//*[@id="ABOUT_TAB"]/div[2]/div[3]/div/div/div[2]/div[2]/div/div/text()').extract()
            hotel_feature = ",".join(feature + feature_with_instr)

        except:
            hotel_feature = None
        hotel['feature'] = hotel_feature
        print(hotel_feature)

        # 客房类型
        try:
            # 不带说明
            r_type = response.xpath(xpath_room_type).extract()

            # 带说明
            r_type_instr = response.xpath(
                '//*[@id="ABOUT_TAB"]/div[2]/div[4]/div[2]/div[1]/div[4]/div/text()').extract()

            room_type = ",".join(r_type + r_type_instr)

        except:
            room_type = None

        hotel['room_type'] = room_type
        print(room_type)

        # 酒店星级
        try:
            star = "".join(re.findall('\d+', response.xpath(xpath_star).extract_first()))
        except:
            star = None
        hotel['star'] = star
        print(star)

        # 房间数量
        try:
            # 不带说明
            rooms = response.xpath(xpath_rooms).extract()
            # 带说明
            rooms_instr = response.xpath('//*[@id="ABOUT_TAB"]/div[2]/div[4]/div[2]/div[3]/div[2]/div/text()').extract()
            rooms = ",".join(rooms + rooms_instr)
        except:
            rooms = -1
        hotel['rooms'] = rooms
        print(rooms)

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
            pass

        hotel['youhui'] = prices

        hotel['hotel_city'] = ''
        hotel['hotel_id'] = ''

        #

        # if __name__ == '__main__':
        #     # hotel_detail_url = "/Hotel_Review-g294212-d595677-Reviews-Park_Plaza_Wangfujing-Beijing.html"
        #     # url = pre_url + hotel_detail_url
        #     # code = re.findall('d\d+(?=-)', url)[0]
        #     # print(code)
        #
        #     # url_start = re.search('.+Reviews', url)
        #     # review_page_urls = []
        #     # review_page_urls.append(url)
        #     # for n in range(1, math.ceil(20 / 5)):
        #     #     review_page_url = re.sub('.+Reviews', url_start.group() + '-or' + str(n * 5), url)
        #     #     review_page_urls.append(review_page_url)
        #     #     print(review_page_url)
        #     str1 = '排名第53'
        # str2 = '在6,648家'
        # print("".join(re.findall('\d+', str1)))
        # print("".join(re.findall('\d+', str2)))


