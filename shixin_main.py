# *_*coding=utf-8*_*


from shixin import get_http
import time
import random
from multiprocessing import Pool
from redis import StrictRedis, exceptions
from multiprocessing.dummy import Pool as thread_pool
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)
redis = StrictRedis(host='localhost', port=6379, db=0)


def list_name():  # 从redis数据库中提取信息
    time.sleep(2)
    tname = []
    for num in range(1, 6):
        names = redis.spop('shixin')  # 随机返回并删除key为name的set中一个元素
        if names != None:
            name = str(names, encoding='utf-8')
            tname.append(name)
        if names == None:
            print('等待添加')
            time.sleep(1)
            continue
    print('开始查询')
    run_main(tname)
    print('查询完毕')
    return list_name


def run_main(names):
    pool = thread_pool(3)
    pool.apply_async(get_http, names)
    pool.close()
    pool.join()


if __name__ == '__main__':
    while True:
        try:
            list_name()
        except exceptions.ConnectionError:
            print('等待连接redis数据库')
            time.sleep(30)



