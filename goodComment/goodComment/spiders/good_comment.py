#coding=utf8
import re
import json
from scrapy.selector import Selector
import scrapy
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle
from goodComment.items import GoodcommentItem
import logging
import sys

def getRegex(pattern, content):
	group = re.search(pattern, content)
	if group:
		return group.groups()[0]
	else:
		return ''


def printUrl(func):
	def parser(self, response):  # self是函数传入的家伙
		print response.url
		#print "Arguments were: %s, %s" % (args, kwargs)
		return func(self, response)  # 2
	return parser


class GoodCommentSpider(Spider):
	name = "good_comment"
	#allowed_domains = ["*"]
	start_urls = [
		"https://www.taobao.com/markets/nvzhuang/taobaonvzhuang?spm=a21bo.2017.201867-main.1.5af911d9kx7N6a" # 女装
	]
	@printUrl
	def parse(self, response):
		urls = re.findall('"cat_href":"(.*?)"',response.body)
		for url in urls:
			yield scrapy.Request(url, self.parse2)

	@printUrl
	def parse2(self, response):
		urls = re.findall('"detail_url":"(.*?)"', response.body)
		for url in urls:
			url = 'https:'+url.decode('raw_unicode_escape')
			yield scrapy.Request(url, self.parse3)

	@printUrl
	def parse3(self, response):
		url = response.url
		logging.info('parsed ' + str(url))
		if 'item.htm' in response.url:
			sel = Selector(response)
			base_url = get_base_url(response)
			print base_url
			catid = getRegex('catid="(\d+)"',response.body)

			item_id = getRegex('id=(\d+)',response.url)
			spuId = getRegex('"spuId":"(\d+)"',response.body)
			sellerId = getRegex('sellerId=(\d+)',response.body)
			rateType = 1 # 好评=1 差评=-1
			if 'taobao.com' in base_url:
				url = 'https://rate.taobao.com/feedRateList.htm?auctionNumId=%s&userNumId=%s&currentPageNum=1&rateType=%s'%(item_id,sellerId,rateType)
			else:
				url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&spuId=%s&sellerId=%s&currentPage=1&rateType=%s'%(item_id,spuId,sellerId,rateType)
			yield scrapy.Request(url, self.parser_comment,meta={"catid":catid,"rateType":rateType})

	@printUrl
	def parser_comment(self,response):
		page = response.body.decode('gbk')
		page = re.search('\((.*)\)', page).group(1)
		catid = response.meta.get('catid', 0)
		rateType = response.meta.get('rateType', 0)
		if 'taobao.com' in response.url:
			comments = json.loads(page)['comments']
			for rateContent in comments:
				rateContent = rateContent['content']  # append 和 appendlist有重复！
				item = GoodcommentItem()
				item['url'] = response.url
				item['rateContent'] = rateContent
				item['catid'] = catid
				item['rateType'] = rateType
				yield item
		elif 'rate.tmall.com' in response.url:
			comments = json.loads(page)['rateDetail']['rateList']
			for rateContent in comments:
				rateContent = rateContent['rateContent']
				item = GoodcommentItem()
				item['url'] = response.url
				item['rateContent'] = rateContent
				item['catid'] = catid
				item['rateType'] = rateType
				yield item




		#批量爬取不知道会发生什么
		#爬下来的没有直接的差评？ 可以过滤一下
		#评论还可以多平台