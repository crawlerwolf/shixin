# *_*coding=utf-8*_*

import requests
import random
from fake_useragent import UserAgent
import time
import re
import json
from Mongo import *
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)

ua = UserAgent()
headers = {
    'Referer':'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&ch=5&tn=98012088_4_dg&wd=%E5%A4%B1%E4%BF%A1%E8%A2%AB%E6%89%A7%E8%A1%8C%E4%BA%BA&rsv_pq=84302d5100007635&rsv_t=4491SqcV8fI0MyG46sVyco5fdkgMRmpq9fOwXzKnYxreD2sekv%2FkaUkKNHYth1Azb5V43Q&rqlang=cn&rsv_enter=1&rsv_sug3=12&rsv_sug1=9&rsv_sug7=101',
    'User-Agent': ua.random}
session = requests.session()


def get_info(info_s):  # 获取数据
    print('提取数据...')
    for info in info_s["data"][0]["result"]:  # 提取数据
        if info['regDate']:
            reg_date = '{}年{}月{}日'.format(info['regDate'][0:4], info['regDate'][4:6], info['regDate'][6:8])
            data = {
                'iname': info['iname'],
                'caseCode': info['caseCode'],
                'cardNum': info['cardNum'],
                'businessEntity': info['businessEntity'],
                'courtName': info['courtName'],
                'areaName': info['areaName'],
                'gistId': info['gistId'],
                'regDate': reg_date,
                'gistUnit': info['gistUnit'],
                'duty': info['duty'],
                'performance': info['performance'],
                'disruptTypeName': info['disruptTypeName'],
                'publishDate': info['publishDate']
            }
            print('存储中...')
            print(data)
            to_mongo(data)
            print('完成储存')
        else:
            data = {
                'iname': info['iname'],
                'caseCode': info['caseCode'],
                'cardNum': info['cardNum'],
                'businessEntity': info['businessEntity'],
                'courtName': info['courtName'],
                'areaName': info['areaName'],
                'gistId': info['gistId'],
                'regDate': info['regDate'],
                'gistUnit': info['gistUnit'],
                'duty': info['duty'],
                'performance': info['performance'],
                'disruptTypeName': info['disruptTypeName'],
                'publishDate': info['publishDate']
            }
            print('存储中...')
            print(data)
            to_mongo(data)
            print('完成储存')
    print('完成数据提取')
    return '完成提取'
# get_http('大连阳光新世纪房地产开发有限公司')


def to_mongo(data):
    while True:
        try:
            ShiXin_info.update({'caseCode': data['caseCode']}, {'$set': data}, True)
            return '完成储存'
        except pymongo.errors.ServerSelectionTimeoutError:
            print('等待连接mongo数据库')
            time.sleep(30)
        except:
            time.sleep(30)


def get_http(name):  # 请求网站
    try:
        url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?'
        params = {'resource_id': 6899,
                  'query': '失信被执行人名单',
                  'cardNum': '',
                  'iname': name,
                  'areaName': '',
                  'ie': 'utf-8',
                  'oe': 'utf-8',
                  'format': 'json',
                  't': int(round(time.time()*1000)),
                  'cb': 'jQuery11020023017826865680435_1510236300897',
                  '_': int(round(time.time()*1000)) - random.randint(2000000, 4000001)}
        time.sleep(random.uniform(6, 8))  # 设置随即时间间隔
        print('查找:', name)
        web_data = requests.get(url, headers=headers, params=params, verify=False, timeout=50)
        web_data.encoding = web_data.apparent_encoding
        if web_data.status_code == 200:  # 获得信息
            info_s = web_data.text
            pattern = re.compile('.*?jQuery.*?\((.*?)}\);', re.S)
            if re.search(pattern, info_s) != None:
                info_s = re.search(pattern, info_s).group(1) + '}'
                info_s = json.loads(info_s)
                if info_s["data"] == []:
                    print('未找到相关失信信息:', name)
                    return '未找到'
                if info_s["data"] != []:
                    print('获取第1页')
                    txt = get_info(info_s)  # 获取数据
                    get_next(name)
                    return txt
        if web_data.status_code != 200:
            txt = get_http(name)
            if txt == '未找到':
                return '未找到'
            if txt == '完成提取':
                return '完成提取'
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
        print('重新请求:', name)
        txt = get_http(name)
        if txt == '未找到':
            return '未找到'
        if txt == '完成提取':
            return '完成提取'
    return get_http


def get_next(name):  # 获取下一页
    for pn in range(10, 201, 10):
        page_num = (pn + 10)//10
        print('请求下一页：第' + str(page_num) + '页')
        params = {'resource_id': 6899,
                  'query': '失信被执行人名单',
                  'cardNum': '',
                  'iname': name,
                  'areaName': '',
                  'ie': 'utf-8',
                  'oe': 'utf-8',
                  'format': 'json',
                  'pn': pn,
                  'rn': 10,
                  't': int(round(time.time() * 1000)),
                  'cb': 'jQuery11020023017826865680435_1510236300897',
                  '_': int(round(time.time() * 1000)) - random.randint(2000000, 4000001)
                  }
        try:
            url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?'
            time.sleep(random.uniform(5, 9))  # 设置随即时间间隔
            web_data = session.get(url, headers=headers, params=params, verify=False, proxies={'http': proxy()}, timeout=500)
            web_data.encoding = web_data.apparent_encoding
            info_s = web_data.text
            pattern = re.compile('.*?jQuery.*?\((.*?)}\);', re.S)
            if re.search(pattern, info_s) != None:
                info_s = re.search(pattern, info_s).group(1) + '}'
                info_s = json.loads(info_s)
                if web_data.status_code == 200:  # 获得信息
                    if info_s["data"] == []:
                        print('未找到:', '第' + str(page_num) + '页', '完成提取')
                        return '未找到'
                    if info_s["data"] != []:
                        get_info(info_s)  # 获取信息
            if web_data.status_code != 200:
                print('提取数据失败')
                for num in range(1,4):
                    txt = get_next_again(name, pn)
                    if txt == '未找到':
                        return '未找到'
                    if txt == '完成提取':
                        return '完成提取'
                continue
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            for num in range(1, 4):
                txt = get_next_again(name, pn)
                if txt == '未找到':
                    return '未找到'
                if txt == '完成提取':
                    return '完成提取'
            continue
    return get_next


def get_next_again(name, pn):  # 获取下一页
    page_num = (pn + 10)//10
    print('重新请求：第' + str(page_num) + '页')
    params = {'resource_id': 6899,
              'query': '失信被执行人名单',
              'cardNum': '',
              'iname': name,
              'areaName': '',
              'ie': 'utf-8',
              'oe': 'utf-8',
              'format': 'json',
              'pn': pn,
              'rn': 10,
              't': int(round(time.time() * 1000)),
              'cb': 'jQuery11020023017826865680435_1510236300897',
              '_': int(round(time.time() * 1000)) - random.randint(2000000, 4000001)
              }
    try:
        url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?'
        time.sleep(random.uniform(5, 9))  # 设置随即时间间隔
        web_data = session.get(url, headers=headers, params=params, verify=False, proxies={'http': proxy()}, timeout=500)
        web_data.encoding = web_data.apparent_encoding
        info_s = web_data.text
        pattern = re.compile('.*?jQuery.*?\((.*?)}\);', re.S)
        if re.search(pattern, info_s) != None:
            info_s = re.search(pattern, info_s).group(1) + '}'
            info_s = json.loads(info_s)
            if web_data.status_code == 200:  # 获得信息
                if info_s["data"] == []:
                    print('未找到:', '第' + str(page_num) + '页', '完成提取')
                    return '未找到'
                if info_s["data"] != []:
                    txt = get_info(info_s)  # 获取信息
                    return txt
        elif web_data.status_code != 200:
            print('提取数据失败')
            return '提取数据失败'
    except(requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
        return get_next_again


if __name__ == '__main__':
    get_http('湖南雁能配电设备有限公司')
