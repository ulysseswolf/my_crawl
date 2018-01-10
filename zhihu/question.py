import re
import requests
import random
from lxml import etree
from pymongo import MongoClient
import html2text
from pymongo.errors import DuplicateKeyError
import sys
sys.path.append('../')
from util.config import Config
from util.Logger import logger
from proxy.rand_proxy import rand_proxy
from util.user_agents import agents

from login import AccountManager
from requestHeader import requestHeader
from answers import per_question


#  work 不能和job放在同一模块中，否则程序会报错

question_p = re.compile('href="(/question/(\d+))">(.*[？]?)</a>')
question_href_p = re.compile('<a class="question_link" href="(/question/\d+)"')
top_answer_p = re.compile('<a href="(/question/(\d+)/answer/(\d+))" class="toggle-expand">显示全部</a>')
max_vote_p = re.compile('<a class="zm-item-vote-count js-expand js-vote-count" href="javascript:;" data-bind-votecount>(\d+)</a>')

def max_page(topic_id, header):
    question_url = 'https://www.zhihu.com/topic/{0}/top-answers'.format(topic_id) 
    err = 0
    while 1:
        user_agent = random.choice(agents)
        proxy = rand_proxy()
        ip = proxy['http'].split(':')[1][2:]
        header.update({'User-Agent': user_agent})
        try:
            response = requests.get(question_url, headers=header, proxies=proxy)
        except Exception as e:
            logger.error(e)
            logger.error(topic_id)
            continue

        logger.info('visit: %s' % question_url)
        if response.status_code != 200:
            logger.error('{0} ERROR'.format(question_url))
            logger.error(header)
            return
        html = response.content.decode('utf-8')
        html_tree = etree.HTML(html)
        page_numbers = html_tree.xpath('//div[@class="zm-invite-pager"]/span/a/text()')
        try:
        # span.text: 上一页 1 2 3 ... 13801 下一页
            return page_numbers[-2]
        except Exception as e:
            if html.find('系统检测到您的帐号或IP存在异常流量') > -1:
                logger.error('统检测到您的帐号或IP存在异常流量, proxy: {0}, user-agent: {1}'.format(proxy, user_agent))
                if err == 5:
                    break
                err += 1
                continue

            logger.error(e)
            logger.error('topic_id: {0}'.format(topic_id))
            return 1

# db.questions.createIndex( { "qid": 1 }, { unique: true } )
def questions_per_page(topic_id, page, header):
    question_url = 'https://www.zhihu.com/topic/{0}/questions?page={1}'.format(topic_id, page) 
    user_agent = random.choice(agents)
    header.update({'User-Agent': user_agent})
    html = requests.get(question_url, headers=header, proxies=rand_proxy()).content.decode('utf-8')
    questions = re.findall(question_p, html)
    for q in questions:
        try:
            mongo_conn().questions.insert_one({'qid': q[1], 'stid': topic_id, 'href': q[0], 'name': q[2]})
        except DuplicateKeyError as e:
            logger.error(e)
            logger.info("topic_id: {0}, href: {1} exists".format(topic_id, q[0]))


# db.answers.createIndex( { "answer": 1, 'question':1 }, { unique: true } )
def top_answers(topic_id, page, header):
    question_url = 'https://www.zhihu.com/topic/{0}/top-answers?page={1}'.format(topic_id, page) 
    proxy = rand_proxy()
    user_agent = random.choice(agents)
    header.update({'User-Agent': user_agent})
    try:
        html = requests.get(question_url, headers=header, proxies=proxy).content.decode('utf-8')
    except Exception as e:
        logger.error('exception url: %s' % question_url)
        logger.error(e)
        top_answers(topic_id, page, header)

    # 查找本页第一个问题的点赞数量，如果小于1000，忽略本页内容
    first_vote = max_vote_p.search(html)
    if first_vote:
        max_vote = first_vote.group(1)
        if int(max_vote) < 1000:
            logger.info('ignore %s, max_vote:%s' % (question_url, max_vote))
            return

    answers = re.findall(top_answer_p, html)
    if len(answers) == 0:
        logger.error('{0} answers not found, proxy: {1}'.format(question_url, proxy))

        return
    logger.info('{0} found answer {1}'.format(question_url, len(answers)))
    for a in answers:
        qid, aid, href = a[1], a[2], a[0]
        try:
            mongo_conn().answers.insert_one({'topic': topic_id, 'question': a[1], 'answer': a[2], 'href': a[0]})
        except DuplicateKeyError as e:
            return
            #logger.error(e)
            #logger.info("topic_id: {0}, href: {1} exists".format(topic_id, a[0]))

# db.top_answers.createIndex( { "href": 1}, { unique: true } )
def questions_per_topic(topic_id, header, rQ):
    for page in range(1, 51):
        topic_url = 'https://www.zhihu.com/topic/%s/top-answers?page=%d' % (topic_id, page)
        proxy = rand_proxy()
        user_agent = random.choice(agents)
        header.update({'User-Agent': user_agent})
        try:
            html = requests.get(topic_url, headers=header, proxies=proxy).content.decode('utf-8')
        except Exception as e:
            logger.error('exception url: %s' % topic_url)
            logger.error(e)
            continue
            #questions_per_topic(topic_id, header, rQ)

    
        # 查找本页第一个问题的点赞数量，如果小于1000，忽略本页内容
        first_vote = max_vote_p.search(html)
        if first_vote:
            max_vote = first_vote.group(1)
            if int(max_vote) < 1000:
                break

        tree = etree.HTML(html)
        questions = tree.xpath('//div[@class="feed-main"]//a[@class="question_link"]')
        #logger.info('topic: %s, page: %s, find %s questions' % (topic_id, page, len(questions)))
        for q in questions:
            rQ.enqueue(per_question, q.attrib['href'])
            


def mongo_conn():
    c = Config()
    mongo = MongoClient(c.get('mongo', 'host'), int(c.get('mongo', 'port')))
    return mongo.zhihu

if __name__ == '__main__':
    #am = AccountManager('ulysseswolf@gmail.com', 'padrino')
    #am.login()
    #cookie = am.load_cookie()
    #requestHeader.update(cookie)
    top_answers('19671022', 1, requestHeader)
    #fetch_answer('/question/48376381', requestHeader)
