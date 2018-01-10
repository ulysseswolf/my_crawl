import random
import redis
import sys
sys.path.append('../')
from util.Logger import logger

def rand_proxy():
    rdb = redis.Redis()
    proxy_size = rdb.llen('valid_proxy')
    if proxy_size == 0:
        logger.error('no available proxies')
        raise RuntimeError('no available proxies')

    randint = random.randint(0, proxy_size-1)
    ip_port = rdb.lrange('valid_proxy', randint, randint)[0].decode('utf-8')
    proxy = {'http': 'http://{0}'.format(ip_port)}
    # {'http': 'http://127.0.0.1:8088'}
    return proxy

if __name__ == '__main__':
    for i in range(10):
        print(rand_proxy())
