# coding=utf-8

import requests
import time
from fake_useragent import UserAgent
from redis import StrictRedis, exceptions


redis = StrictRedis(host='localhost', port=6379, db=0)
ua = UserAgent()
headers = {'User-Agent': ua.random}


# 将公司名称存入redis数据库调用
def get_numbers():  # 查询数据库条数
    url = 'http://localhost:8088/solr/entfind/select?q=*%3A*&start=0&rows=0&wt=json&indent=true&_={}'.format(int(round(time.time()*1000)))  # 所有公司地址
    web_data = requests.get(url, verify=False)
    num = web_data.json()['response']['numFound']
    return int(num)


def get_host_name(num):  # 获取公司名称
    # nums = get_numbers()
    try:
        url = 'http://localhost:8088/solr/entfind/select?'  # 所有公司名称
        for start_num in range(int(num)+100, int(num)+200, 100):
            print(start_num)
            params = {
                'q': '*:*',
                'start': start_num,
                'rows': 100,
                'wt': 'json',
                'indent': 'true',
                '_': int(round(time.time()*1000))
            }
            web_data = requests.get(url, headers=headers, params=params)
            with open('SX_num.txt', 'wb') as f:
                f.write(bytes(str(start_num), encoding='utf-8'))
                f.close()
            name = web_data.json()['response']['docs']
            for each_name in name:
                host_name = each_name['ENTNAME']
                host_name.replace('', '')
                print(redis.sadd('shixin', host_name), host_name)  # 向key为name的set中添加元素
    except:
        get_host_name_again()
    return get_host_name


def get_host_name_again():  # 获取公司名称
    # num = get_numbers()
    with open('SX_num.txt', 'rb') as f:
        num1 = f.read()
        f.close()
    try:
        url = 'http://localhost:8088/solr/entfind/select?'  # 所有公司名称
        for start_num in range(int(num1)+100, int(num1)+200, 100):
            print(start_num)
            params = {
                'q': '*:*',
                'start': start_num,
                'rows': 100,
                'wt': 'json',
                'indent': 'true',
                '_': int(round(time.time()*1000))
            }
            web_data = requests.get(url, headers=headers, params=params)
            with open('SX_num.txt', 'wb') as f:
                f.write(bytes(str(start_num), encoding='utf-8'))
                f.close()
            name = web_data.json()['response']['docs']
            for each_name in name:
                host_name = each_name['ENTNAME']
                host_name.replace('', '')
                print(redis.sadd('shixin', host_name), host_name)  # 向key为name的set中添加元素
    except:
        get_host_name_again()
    return get_host_name_again


def get_name():  # 查询个数是否添加到redis
    num = redis.scard('shixin')  # 查询shixin中key的个数
    if int(num) <= 300:
        get_host_name_again()
    if int(num) >= 900:
        print('等待加入')
        time.sleep(30)
    return num


def get_page():  # 查询是否获取完毕
    with open('SX_num.txt', 'rb') as f:
        num1 = str(f.read(), encoding='utf-8')
        f.close()
    nums = get_numbers()
    if int(num1) > nums:
        return '获取完毕'
    if int(num1) < nums:
        get_name()
    return get_page


if __name__ == '__main__':

    while True:
        try:
            txt = get_page()
            if txt == '获取完毕':
                break
            if txt != '获取完毕':
                continue
        except exceptions.ConnectionError:
            print('等待连接redis数据库')
            time.sleep(30)
        except requests.exceptions.ConnectionError:
            print('等待请求solr')
