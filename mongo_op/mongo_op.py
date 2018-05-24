#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from pymongo import MongoClient

conn = MongoClient('127.0.0.1', 27017)
db = conn.test  #连接mydb数据库，没有则自动创建
my_set = db.good_comment #使用test_set集合，没有则自动创建

good_comments = my_set.find({'rateType':-1}).limit(2000)

with open('bad.txt','w') as f:
    line_no = 1
    for good_comment in good_comments:
        line_no+=1
        f.write('%s\n'%(good_comment['rateContent']))
