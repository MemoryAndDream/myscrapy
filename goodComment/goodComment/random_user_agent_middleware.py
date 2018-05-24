#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: xieguanfu
@contact: xieguanfu@maimiaotech.com
@date: 2017-11-30 16:23
@version: 0.0.0
@license: Copyright Maimiaotech.com
@copyright: Copyright Maimiaotech.com

"""


from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

class RandomUserAgentMiddleware(UserAgentMiddleware):

    #def __init__(self,user_agent):
    #    self.user_agent = user_agent

    #@classmethod
    #def from_crawler(cls, crawler):
    #    #可以在设置里面自定义user_agent列表选项进行重新user_agent
    #    return cls(crawler.settings.get('MY_USER_AGENT'))

    def process_request(self,request,spider):
        from .user_agent_pool import get_random_user_agent
        agent = get_random_user_agent()
        request.headers['User-Agent'] = agent

