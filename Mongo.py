# *_*coding=utf-8*_*

import pymongo

client = pymongo.MongoClient('localhost', 27018)

ShiXin = client['ShiXin']

ShiXin_info = ShiXin['ShiXin_info']  # 已获取失信信息的公司

ShiXin_name = ShiXin['ShiXin_name']  # 需获取爬去的公司名称

ShiXin_none = ShiXin['ShiXin_none']  # 未查询到失信信息的公司

ShiXin_num = ShiXin['ShiXin_num']  # 获取公司信息时报400错误

ShiXin_un_info = ShiXin['ShiXin_un_info']  # 获取公司信息时报错
