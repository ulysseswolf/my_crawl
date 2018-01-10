from redis import Redis
from pymongo import MongoClient
import os
import multiprocessing
from rq import Worker, Queue, Connection
import sys
sys.path.append('../')
from login import AccountManager
from util.config import Config
from util.Logger import logger
from requestHeader import requestHeader
from question import questions_per_topic

# rq worker with multiprocessing
conn = Redis()
#listen=['high','default','low']
listen=['default']
#listen=['failed']
def worker():
    with Connection(conn):
        worker=Worker(map(Queue,listen))
        worker.work()

def run_worker(count=10):
    pool = multiprocessing.Pool(processes=count)
    for i in range(count):
        pool.apply_async(worker,)

    pool.close()
    pool.join()


def main():
    c = Config()
    mongo = MongoClient(c.get('mongo', 'host'), int(c.get('mongo', 'port')))
    #am = AccountManager()
    #cookie = am.load_cookie()
    #requestHeader.update(cookie)
    rQ = Queue(connection=Redis())
    #cursor = mongo.zhihu.sub_topic.find({}, {'sub_tid': 1, '_id': 0}, no_cursor_timeout=True).skip(32).limit(200)
    cursor = mongo.zhihu.sub_topic.find({}, {'sub_tid': 1, '_id': 0}).skip(150).limit(20000).batch_size(10)
    for subtopic in cursor:
        stid = subtopic['sub_tid']

        #mongo.zhihu.sub_topic.update_one({'sub_tid': stid}, {'$set': {'max_page': page_no}})
        #rQ.enqueue(questions_per_page, stid, requestHeader)
        questions_per_topic(stid, requestHeader, rQ)

    logger.info('done')
    #run_worker(3)


if __name__ == '__main__':
    p1 = multiprocessing.Process(target=main)
    p2 = multiprocessing.Process(target=run_worker, args=(5,))
    p1.start()
    p2.start()
    #run_worker(5)
