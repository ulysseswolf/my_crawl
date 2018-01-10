import re
import requests
import random
import time
from lxml import etree
from pymongo import MongoClient
import html2text
from pymongo.errors import DuplicateKeyError
import sys
sys.path.append('../')
from util.config import Config
from util.Logger import logger
from login import AccountManager
from proxy.rand_proxy import rand_proxy
from util.user_agents import agents

from requestHeader import requestHeader

# https://www.zhihu.com/question/39389863
def per_question(q_href):
#def per_question(q_href, cookie):
    time.sleep(random.randint(1,8))
    q_url = 'https://www.zhihu.com%s' % q_href
    proxy = rand_proxy()
    user_agent = random.choice(agents)
    header = requestHeader
    header.update({'User-Agent': user_agent})
    try:
        #response = requests.get(q_url, headers=header, proxies=proxy, cookies=cookie).content
        response = requests.get(q_url, headers=header, proxies=proxy).content
        html = response.decode('utf-8')
    except Exception as e:
        logger.error('exception url: %s' % q_url)
        logger.error(e)
        #logger.info(response)
        #sys.exit()
        per_question(q_href)

    #if '系统检测到您的帐号或IP存在异常流量' in html:
    #    logger.error('proxy error, {0}'.format(proxy))
    #    raise Exception

    tree = etree.HTML(html)
    tags = tree.xpath('//div[@class="Popover"]/text()')
 
    #question_a = tree.xpath('//h1[@class="QuestionHeader-title"]/text()')
    question_a = tree.xpath('//title[@data-react-helmet="true"]/text()')
    if question_a:
        title = question_a[0].replace(' - 知乎', '')
        if '安全验证' == title:
            logger.error('proxy error, {0}'.format(proxy))
            raise Exception

        logger.info(title)
    else:
        logger.error('%s title not found' % q_url)
        if '你正在使用的浏览器版本过低' in html:
            logger.info(user_agent)
            per_question(q_href)
        else:
            raise Exception
 
    #detail_a = tree.xpath('//div[@class="QuestionHeader-detail"]/div/div/span/text()')
    #if detail_a:
    #    content = detail_a[0]
    #else:
    #    content = None
 
    topics = tree.xpath('//a[@class="TopicLink"]')
    sub_topic = mongo_conn().sub_topic
    for t in topics:
        # https://www.zhihu.com/topic/19552832
        tid = t.attrib['href'].split('/')[-1]
        name = t.xpath('.//text()')[0]
        try:
            sub_topic.insert_one({'sub_tid': tid, 'sub_name': name})
        except DuplicateKeyError as e:
            continue
 
    items = tree.xpath('//div[@class="ContentItem AnswerItem"]')
    for i in items:
        # "1792 人赞同了该回答"
        vote_text = i.xpath('.//span[@class="Voters"]/button/text()')
        if len(vote_text) == 0:
            logger.info('%s no votes' % q_url)
            break

        vote_num = re.match('\d+', vote_text[0]).group()
        if int(vote_num) >= 800:
            href = i.xpath('.//meta[@itemprop="url"]')[1].attrib['content']
            answer = i.xpath('.//span[@class="RichText CopyrightRichText-richText"]')[0]
            s = etree.tostring(answer).decode('utf-8')
            body = html2text.html2text(s.replace('<br>', ''))
 
            try:
                mongo_conn().top_answers.insert_one({'title': title, 'answer': body, 'href': href, 'vote': vote_num})
            except DuplicateKeyError as e:
                continue



def mongo_conn():
    c = Config()
    mongo = MongoClient(c.get('mongo', 'host'), int(c.get('mongo', 'port')))
    return mongo.zhihu

if __name__ == '__main__':
    am = AccountManager()
    cookie = am.load_cookie()
    per_question('/question/37709843', cookie)

