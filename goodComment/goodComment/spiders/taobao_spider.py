#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: xieguanfu
@contact: xieguanfu@maimiaotech.com
@date: 2017-11-20 18:34
@version: 0.0.0
@license: Copyright Maimiaotech.com
@copyright: Copyright Maimiaotech.com

"""


import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import sys,os,re,urllib
import requests
import simplejson as json
import time
from datetime import datetime
from spider_service.common.tools import RequestHandle,ResponseTool
from lxml import html as lhtml
from scrapy.log import logger


class TBItemSpider(scrapy.Spider):
    name = "taobao"

    def __init__(self, name=None, **kwargs):
        if not kwargs or ('keyword' not in kwargs and 'num_iid' not in kwargs):
            raise Exception('spider must input params,eg:scrapy runspider  -a keyword=连衣裙 -a num_iid=563367957687 taobao_spider.py')
        super(TBItemSpider,self).__init__(name,**kwargs)
        self.params = kwargs

    #rules = (
    #    Rule(LinkExtractor(allow=('list.html?cat=670,671,672&page=([\d]+)', ),),callback='parse_ob',
    #            follow=True)
    #)

    def start_requests(self):
        urls = [
            #'https://s.taobao.com/list?spm=a217l.8087239.620327.1.25258388JF3Nts&q=%E7%94%B5%E9%A5%AD%E7%85%B2&style=grid&seller_type=taobao'
            'https://re.taobao.com/search?spm=a230r.1.1957635.81.12a5fbfbJzZ7Dy&keyword=%C1%AC%D2%C2%C8%B9&frontcatid=&isinner=1&refpid=420434_1006',
        ]
        now = datetime.now()
        for key,value in self.params.iteritems():
            if 'keyword' ==key :
                url = 'https://re.taobao.com/search?spm=a230r.1.1957635.81.12a5fbfbJzZ7Dy&keyword=%s&frontcatid=&isinner=1&refpid=420434_1006' %(value)
                spider_name = '%s_%s' %(hash(url),time.mktime(now.utctimetuple()))
                yield scrapy.Request(url=url, callback=self.parse,meta = {'keyword':self.params['keyword'],'spider_name':spider_name})
            elif 'num_iid' == key:
                url = 'https://item.taobao.com/item.htm?spm=a230r.1.14.257.6274ebf9sIiAqt&id=%s&ns=1&abbucket=13#detail' % value
                spider_name = '%s_%s' %(hash(url),time.mktime(now.utctimetuple()))
                yield scrapy.Request(url=url, callback=self.parse_item,meta = {'num_iid':int(self.params['num_iid']),'spider_name':spider_name,'dont_redirect':True,'handle_httpstatus_list': [301,302]})

    def parse(self,response):
        from spider_service.items import RankItem
        selector = scrapy.Selector(response)

        if 're.taobao.com/search'  in response.url:
            item_list = selector.xpath('//div[@id="J_waterfallPagination"]//div[@class="pagination-page"]/a')
            item_list = selector.xpath('//div[@id="J_waterfallWrapper"]/div[@class="item"]')
            data_obj = RankItem()
            rank = 1
            spider_name = response.meta.get('spider_name')
            keyword = response.meta.get('keyword')
            for item in item_list:
                click_url = item.xpath('./a/@href').extract_first()
                img_url = item.xpath('./a//img/@data-ks-lazyload').extract_first() 
                price = item.xpath('./a/div[@class="info"]/p[@class="price"]/span/strong/text()').extract_first()
                title = item.xpath('./a/div[@class="info"]/span[@class="title"]/@title').extract_first()
                nick = item.xpath('./a/div[@class="info"]/p[@class="shopName"]/span[@class="shopNick"]/text()').extract_first().replace('\n','').strip()
                pay_count = item.xpath('.//span[@class="payNum"]/text()').extract_first()
                if pay_count:
                    pay_count = pay_count.replace('人付款'.decode('utf8'),'')

                doc = {'rank':rank,'click_url':click_url,'img_url':img_url,'price':price,'title':title,"nick":nick,'pay_count':pay_count,'keyword':keyword,'spider_name':spider_name}
                data_obj.update(doc)
                #print nick,price,title
                rank += 1
                yield data_obj
                #yield scrapy.Request(url = click_url,meta = {'WEBKIT':'PhantomJS'},callback = self.parse_item)
                yield scrapy.Request(url = click_url,meta = {'data':doc},callback = self.parse_item)

    def parse_item(self,response):
        from spider_service.items import TBItem
        from spider_service.common.tools import LevelTool
        selector = scrapy.Selector(response)
        data_obj = TBItem()
        item_rsp_text = response.body_as_unicode()
        if response.status  in [302,301]:
            redirect_url = response.url
            if response.headers.get('Location') and 'login.taobao.com/jump?target=' in response.headers.get('Location') and 'login.taobao.com/jump' not in response.url:
                redirect_url = response.headers.get('Location')
            item_rsp = RequestHandle.get_rsp(redirect_url)
            item_rsp_text = item_rsp.text
            selector = scrapy.Selector(item_rsp)

        if 'detail.tmall.com/item.htm' in response.url or 'tmall.com' in response.url or True:
            title = selector.xpath('//h3[@class="tb-main-title"]/@data-title').extract_first()
            if not title:
                title = selector.xpath('//input[@name="title"]/@value').extract_first()
            if not title:
                logger.info('no find title ,response url:' + response.url)
                return
            #原始价格,促销价格获取经常需验证
            price = response.xpath("//em[@class='tb-rmb-num']/text()").extract_first()
            nick = selector.xpath('//div[@class="tb-shop-info-wrap"]/div/div[@class="tb-shop-seller"]//a[@class="tb-seller-name"]/text()').extract_first()
            nick_tmc = selector.xpath('//a[@class="slogo-shopname"]/strong/text()').extract_first()
            nick = nick_tmc if not nick and nick_tmc else nick
            shop_type ='B' if nick_tmc else 'C'
            if nick:
                nick = nick.replace('\n','').strip()
            else:
                #企业店铺店铺等级信息需要单独获取
                nick_list = re.findall('''[^\w]*sellerNick\s*:\s*['"](.+)['"]''',response.body)
                if not nick_list:
                    return
                nick = urllib.unquote_plus(nick_list[0]).decode('gbk') if nick_list else nick
            #比如用户是3皇冠,知道是3,但是不知道是皇冠还是钻,因为图片是在css属性中的background中
            level_type = selector.xpath('//div[@class="tb-shop-info-hd"]/div[2]/@class').extract_first()
            level_num = len(selector.xpath('//div[@class="tb-shop-info-hd"]/div[2]//i'))
            rate_url = selector.xpath('//div[@class="tb-shop-info-hd"]/div[2]//a/@href').extract_first()
            ##price_url like https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId=559466494297&sellerId=96216586&modules=dynStock,qrcode,viewer,price,duty,xmpPromotion,delivery,upp,activity,fqg,zjys,amountRestriction,couponActivity,soldQuantity,originalPrice,tradeContract
            price_url_list = re.findall('''[^\w]*wholeSibUrl\s*:\s*['"](.+)['"]''',response.body)
            count_url_list = re.findall('''[^\w]*counterApi\s*:\s*['"](.+)['"]''',response.body)
            #企业店铺延迟加载
            shop_info_url_list = re.findall('''[^\w]*api\s*:\s*['"](.+alicdn\.com/asyn\.htm.*)['"]''',response.body)
            user_id = selector.xpath('//div[@id="J_Pine"]/@data-sellerid').extract_first()
            #c店
            if shop_type == 'B':
                num_iid = selector.xpath('//div[@id="LineZing"]/@itemid').extract_first()
                sid = selector.xpath('//div[@id="LineZing"]/@shopid').extract_first()
                cid_str = selector.xpath('//div[@id="J_ZebraPriceDesc"]/@mdv-cfg').extract_first()
                m = re.findall('catId:(\d+)',cid_str)
                if not m:
                    return
                cid = m[0] if m else ''
                js_data = re.findall('<\s*script[^>]*>[^<]*TShop.Setup\(([^<]*?)\)[^<]*<\s*/\s*script\s*',item_rsp_text)
                js_data = json.loads(js_data[0]) if js_data else {}
                user_id = js_data['itemDO']['userId']
                cid = js_data['itemDO']['categoryId']
                shop_info_url_list = [js_data['api']['fetchDcUrl']]
                price = js_data['detail']['defaultItemPrice'] 
                count_url_list = [js_data['apiBeans']]

            else:
                num_iid = selector.xpath('//div[@id="J_Pine"]/@data-itemid').extract_first()
                sid = selector.xpath('//div[@id="J_Pine"]/@data-shopid').extract_first()
                cid = selector.xpath('//div[@id="J_Pine"]/@data-catid').extract_first()
            detail_common_url = 'https://rate.taobao.com/detailCommon.htm?auctionNumId=%s&userNumId=%s' %(num_iid,user_id) + '&ua=098%23E1hvopvUvbpvUpCkvvvvvjiPPLFpsjDCPFSwsjthPmPh6j3CP2ShljnCPLShlj3UR4wCvvpvvUmmmphvLCCwXQvjOezOafmAdcOdYExrt8g7EcqyaNoxdB%2BaWXxrzjZcR2xVI4mxfXAK4Z7xfa3l5dUf85xr1jZ7%2B3%2BuaNLXSfpAOHmQD7zydiTtvpvIvvvvvhCvvvvvvUnvphvUivvv96CvpC29vvm2phCvhhvvvUnUphvp98yCvv9vvUvQ0%2FCUhOyCvvOWvvVvaZUCvpvVvmvvvhCv2QhvCPMMvvvtvpvhvvvvvv%3D%3D&callback=json_tbc_rate_summary'
            detail_common_rsp = RequestHandle.get_json_rsp(detail_common_url)
            detail_common_dict = ResponseTool.unpack_jsonp(detail_common_rsp.text)
            if price_url_list:
                price_url = 'https:'+ price_url_list[0]
                #yield scrapy.Request(url=price_url,meta = {'data':doc,'cookiejar':1},callback = self.parse_price)
            count_dict = {}
            if count_url_list:
                count_url= 'https:'+count_url_list[0] + '&callback=jsonp109'
                count_rsp = RequestHandle.get_json_rsp(count_url)
                try:
                    count_dict = ResponseTool.unpack_jsonp(count_rsp.text)
                except Exception,e:
                    m_count = re.findall('ICCP_1_%s":(\d*)' % num_iid, count_rsp.text)
                    if m_count:
                        count_dict = {'ICCP_1_%s' % num_iid:int(m_count[0])}
            #企业店铺,店铺信息异步加载
            prom_price = None
            if 'tb-shop-info-wrap' not in response.body and title and nick and shop_info_url_list:
                shop_info_url = 'https:' + shop_info_url_list[0]
                shop_text = RequestHandle.get_rsp(shop_info_url).text.replace('\\r\\n','').replace('\\"','"').replace("\\'","'")
                m = re.findall('(<div class="tb-shop".*)',shop_text)
                if m:
                    page = lhtml.document_fromstring(m[0])
                #if shop_type == 'B':
                #    page = lhtml.document_fromstring(shop_text)
                #    prom_price_list = page.xpath('//p[@class="price"]/span/text()') 
                #    prom_price = prom_price_list[0] if prom_price_list else None
                if m:
                    level_num = len(page.xpath('//div[@class="shop-rank-wrap"]/span/a/i'))
                    level_type_obj = page.xpath('//div[@class="shop-rank-wrap"]/span/a') 
                    level_type = level_type_obj[0].get('class') if level_type_obj else level_type 
                page.xpath('//p[@class="price"]/span/text()')
            level = LevelTool.get_level(level_num,level_type)
            #print '===item==',nick,level_num,title,rate_url,price_url_list
            doc = {'nick':nick,'level':level,'item_title':title,'origin_price':price}
            if response.meta.get('data'):
                doc.update(response.meta.get('data'))
            doc.update({'user_id':int(user_id),'num_iid':int(num_iid),'sid':int(sid),'cid':int(cid),'common_detail':detail_common_dict,'count_detail':count_dict})
            data_obj.update(doc)
            yield data_obj
                
