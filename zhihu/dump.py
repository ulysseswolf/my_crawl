import os
import sys
from pymongo import MongoClient

sys.path.append('../')
from util.config import Config
from util.Logger import logger

file_dir = os.path.abspath('./files')
def dump():
    c = Config()
    mongo = MongoClient(c.get('mongo', 'host'), int(c.get('mongo', 'port')))
    for i in range(570):
        cursor = mongo.zhihu.top_answers.find({}).skip(i*100).limit(100)
        file_name = os.path.join(file_dir, '2017-12-01-answers-%d.md' % i)
        with open(file_name, 'a') as md:
            md.write("---\nlayout: post\ntitle: 'answers %d'\ntags: [zhihu]\n---\n" % i)
            for answer in cursor:
                md.write("## [%s](%s)\n" % (answer['title'], answer['href']))
                md.write("%s\n" % answer['answer'])

def dump_questions():
    c = Config()
    mongo = MongoClient(c.get('mongo', 'host'), int(c.get('mongo', 'port')))
    cursor = mongo.zhihu.top_answers.find({}, {'title': 1, 'href': 1, '_id': 0})
    file_name = os.path.join(file_dir, '2017-12-01-questions-1.md')
    with open(file_name, 'a') as md:
        md.write("---\nlayout: post\ntitle: 'questions'\ntags: [zhihu]\n---\n")
        for q in cursor:
            md.write("### [%s](%s)\n" % (q['title'], q['href']))




if __name__ == '__main__':
    #dump_questions()
    dump()
