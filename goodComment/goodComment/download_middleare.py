#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: xieguanfu
@contact: xieguanfu@maimiaotech.com
@date: 2017-11-24 15:49
@version: 0.0.0
@license: Copyright Maimiaotech.com
@copyright: Copyright Maimiaotech.com

"""



import sys  
import logging
from scrapy.http import HtmlResponse  
from selenium import webdriver
from multiprocessing import Lock

class WebkitDownloader( object ):  

    def __init__(self):
        self.WEBKIT = None
        self.lock = Lock()
        self.request_count = 0
        #请求次数达到此值,将重启WEBKIT
        self.reset_request_size = 1000


    def process_request( self, request, spider):  
        if request.meta.get('WEBKIT') == 'PhantomJS':
            if not self.WEBKIT:
                self.lock.acquire()
                self.WEBKIT = webdriver.PhantomJS()
                logging.info('create new WEBKIT')
                self.lock.release()
            elif self.request_count >self.reset_request_size:
                self.lock.acquire()
                self.WEBKIT = webdriver.PhantomJS()
                self.reset_request_size = 0
                logging.info('reset_request_size:%s ,request_count:%s neeed restart WEBKIT' %(self.reset_request_size,self.request_count))
                self.lock.release()
            self.WEBKIT.get(request.url)
            body = self.WEBKIT.page_source
            self.request_count += 1
            return HtmlResponse( request.url, body=body.encode('utf8'))  
