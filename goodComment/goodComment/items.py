# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GoodcommentItem(scrapy.Item):  #保存下宝贝的类目信息
    url = scrapy.Field()
    title = scrapy.Field()
    sid = scrapy.Field()
    rateContent = scrapy.Field()
    catid = scrapy.Field()
    rateType = scrapy.Field()

    pass


class ChouqianItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    title = scrapy.Field()
    page_url = scrapy.Field()
    desc = scrapy.Field()
    img_url = scrapy.Field()
    pass