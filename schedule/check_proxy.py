from threading import Thread
import redis
import time
import sys
sys.path.append('../')
from util.config import Config
from proxy.ProxyFilter import validate_proxy
from util.Logger import logger

def task():
    rdb = redis.Redis()
    while 1:
        p = rdb.rpop('valid_proxy')
        if p == None:
            time.sleep(300)
            continue
        p = p.decode('utf-8')
        if validate_proxy(p):
            rdb.lpush('valid_proxy', p)


def check_proxy(threads=10):
    logger.info('start checking proxy')
    t_list = []
    for i in range(threads):
        t = Thread(target=task, args=())
        t_list.append(t)

    for t in t_list:
        t.start()
        t.join()




