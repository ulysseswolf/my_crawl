import re
import requests
import redis
import random
from pymongo import MongoClient
import json
#from threading import Thread
import sys
sys.path.append('../')
from util.config import Config
from util.Logger import logger
from login import AccountManager
from requestHeader import requestHeader
from proxy.rand_proxy import rand_proxy

subTopic_url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
subTopic_p = re.compile('href="/topic/(\d+)">\n<img src=".*" alt="(.*)">')


def getTopics():
    url = 'https://www.zhihu.com/topics'
    c = Config()
    account = AccountManager(c.get('zhihu', 'email'), c.get('zhihu', 'password'))
    session = requests.session()
    session.headers = requestHeader
    session.cookies.update(account.load_cookie())
    
    response = session.get(url)
    pattern = re.compile('<li class="zm-topic-cat-item" data-id="(\d+)"><a href="#(.*)?">')
    results = re.findall(pattern,response.text)

    logger.info(results)
    for t in results:
        yield(t)
        #db['topic'].insert_one({'tid': t[0], 'tname': t[1]})

    session.close()

def getSubTopics(topic_id):
    offset = 0

    while 1:
        form_data = {'method': 'next', 'params': '{"topic_id": %s, "offset": %s, "hash_id": ""}' % (topic_id, offset)}
        try:
            response = requests.post(url=subTopic_url, data=form_data, headers=requestHeader, proxies=rand_proxy())
            datas = response.content.decode('utf-8')
            jr = json.loads(datas)
            # convert string array to string
            body = ''.join(jr['msg'])
            items = subTopic_p.findall(body)
            if len(items) == 0:
                break

            for item in items:
                #logger.info(item[0], item[1])
                yield(item)

            offset += 20
        except Exception as e:
            # A 400 means that the request was malformed. 
            # In other words, the data stream sent by the client to the server didn't follow the rules
            logger.error(e)
            logger.info('args -> topic_id: {0}, offset: {1}'.format(topic_id, offset))


def main():
    c = Config()
    mongo = MongoClient(c.get('mongo', 'host'), int(c.get('mongo', 'port')))
    am = AccountManager(c.get('zhihu', 'email'), c.get('zhihu', 'password'))
    cookie = am.load_cookie()
    requestHeader.update(cookie)
    mdb = mongo.zhihu
    for topic in mdb.topic.find():
        tid = topic['tid']
        logger.info('get sub topics of {0}'.format(tid))
        for subtopic in getSubTopics(tid):
            mdb.sub_topic.insert_one({'sub_tid': subtopic[0], 'sub_name': subtopic[1]})

def test():
    c = Config()
    mongo = MongoClient(c.get('mongo', 'host'), int(c.get('mongo', 'port')))
    mdb = mongo.zhihu
    s = mdb.sub_topic
    info = ('19848294', '脑波游戏')
    mdb.sub_topic.insert_one({'sub_tid': info[0], 'sub_name': info[1]})

if __name__ == '__main__':
    #getTopics()
    #getSubTopics(253)
    main()
    #test()

