# -*- coding: utf-8 -*-
# !/usr/bin/env python

'''
self.name为Redis中的一个key
use set
'''

import json
import random
import redis
import sys
sys.path.append('../')
from util.classes import Singleton

class RedisClient:
    __metaclass__ = Singleton
    """
    Reids client
    """

    def __init__(self, host='127.0.0.1', port=6379, name):
        """
        init
        :param name:
        :param host:
        :param port:
        :return:
        """
        self.name = name
        self.__conn = redis.Redis(host=host, port=port, db=0)

    def get(self):
        """
        get random result
        :return:
        """
        #keys = self.__conn.hkeys(self.name)
        #return random.choice(keys).decode('utf-8')
        #return self.__conn.srandmember(self.name).decode('utf-8')

    def lpop(self):
        p = self.__conn.lpop(self.name)
        if p:
            return p.decode('utf-8')
        return None

    def rpop(self):
        p = self.__conn.rpop(self.name)
        return p.decode('utf-8') if p else None

    def lpush(self, value):
        self.__conn.lpush(self.name, value)

    def llen(self, key=None):
        return self.__conn.llen(key or self.name)

    def lrem(self, key, count, val):
    	# LREM list -2 "hello" will remove the last two, 0 means remove all that equal to value
        return self.__conn.lrem(key, num=count, value=val)

    def put(self, key):
        return self.__conn.sadd(self.name, key)

    def spop(self):
        """
        pop an item
        :return:
        """
        p = self.__conn.spop(self.name)
        if p:
            return p.decode('utf-8')
        else:
            return None

    def delete(self, key):
        """
        delete an item
        :param key:
        :return:
        """
        self.__conn.srem(self.name, key)

    def getAll(self):
        # python3 redis返回bytes类型,需要解码
        #if sys.version_info.major == 3:
        #    return [key.decode('utf-8') for key in self.__conn.hgetall(self.name).keys()]
        return [m.decode('utf-8') for m in self.__conn.smembers(self.name)]

    def scard(self, key=None):
        if not key:
            key = self.name
        return self.__conn.scard(key)

    def changeTable(self, name):
        self.name = name


if __name__ == '__main__':
    redis_con = RedisClient('localhost', 6379, 'valid_proxy')
    redis_con.size('valid_proxy')
    # redis_con.put('abc')
    # redis_con.put('123')
    # redis_con.put('123.115.235.221:8800')
    # redis_con.put(['123', '115', '235.221:8800'])
    # print(redis_con.getAll())
    # redis_con.delete('abc')
    # print(redis_con.getAll())

    # print(redis_con.getAll())
    #redis_con.changeTable('raw_proxy')
    #redis_con.put('132.112.43.221:8888')
    #redis_con.pop()

    print(redis_con.get())
