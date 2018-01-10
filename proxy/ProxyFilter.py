import requests
import re
import time
import sys
import redis

sys.path.append('../')
from util.Logger import logger

# 代理 IP 验证网站
url = 'http://icanhazip.com/'
# 请求头信息
header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Encoding': 'gzip, deflate, sdch',
          'Accept-Language': 'zh-CN,zh;q=0.8',
          'Cache-Control': 'max-age=0',
          'Host': 'www.icanhazip.com',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/56.0.2924.87 Safari/537.36'}

# 连接超时设置（单位：秒）
CONNECT_TIMEOUT = 30
# 连接重试次数
NETWORK_RECONNECT_TIMES = 2

RAW_PROXY_QUEUE = 'raw_proxy'
VALID_PROXY_QUEUE = 'valid_proxy'

class ProxyFilter:
    def __init__(self):
        self.db = redis.Redis()

    def run(self):
        ip_port = self.db.rpop(RAW_PROXY_QUEUE)
        if ip_port:
            # redis取出的值是byte类型
            if validate_proxy(ip_port.decode('utf-8')):
                #logger.info('{0} valid'.format(proxy))
                self.db.lpush(VALID_PROXY_QUEUE, ip_port)

            self.run()
        else:
            time.sleep(300)


def validate_proxy(ip_port):
    proxy = {'http': 'http://{0}'.format(ip_port)}
    try:
        html = requests.get('http://httpbin.org/ip', proxies=proxy, headers=header, timeout=10).text
        result = eval(html)['origin']
        # only high anonymous
        if len(result.split(',')) == 2:
            return False

        if result in ip_port:
            return True
        
    except Exception as e:
        return False


def validate_proxy_(ip_port):
    proxy = {'http': 'http://{0}'.format(ip_port)}
    try:
        response = requests.get(url, timeout=CONNECT_TIMEOUT, headers=header, proxies=proxy)
        if response.status_code != 200:
            return False

        if response.content.decode('utf-8').find(ip_port.split(':')[0]) > -1:
            return True
        else:
            return False
    except Exception as e:
        #logger.info(e)
        return False

        
