import time
import redis
import sys
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('../')
from proxy.ProxyGetter import ProxyGetter
from proxy.ProxyFilter import ProxyFilter
from threading import Thread
from util.Logger import logger

def task():
    p = ProxyFilter()
    p.run()

def crawl_and_check(process_num=20):
    logger.info('start crawling proxies')
    crawler = ProxyGetter()
    crawler.crawl_proxies()
    logger.info('end crawling')
    
    logger.info('start cleaning proxies')
    threads = []
    for p in range(process_num):
       proc = Thread(target=task, args=())
       proc.start()
       threads.append(proc)

    for t in threads:
       t.join()

    logger.info('cleaning proxies complete')
    rdb = redis.Redis()
    logger.info('valid_proxy pool size: {0}'.format(rdb.llen('valid_proxy')))
    
def run():
    crawl_and_check()
    sch = BlockingScheduler()
    sch.add_job(crawl_and_check, 'interval', minutes=25)
    sch.start()

if __name__ == '__main__':
    run()
