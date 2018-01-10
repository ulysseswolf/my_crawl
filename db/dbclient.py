import os
import sys
sys.path.append('../')
from util.config import Config
from util.utilclasses import Singleton
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class DBClient:
    __metaclass__ = Singleton
    
    def __init__(self):
        self.config = Config()
        if self.config.db_type == 'SSDB':
            __type = 'SsdbClient'
        elif self.config.db_type == 'redis':
            __type = 'RedisClient'

        self.client = getattr(__import__(__type), __type)(host=self.config.db_host, port=self.config.db_port, name=self.config.db_name)

    def get(self, *key, **kwargs):
        return self.client.get(*key, **kwargs)

    def put(self, key, **kwargs):
        return self.client.put(key, **kwargs)

    def delete(self, key, **kwargs):
        return self.client.delete(key, **kwargs)

    def changeTable(self, name):
        return self.client.changeTable(name)

    def exists(self, key, **kwargs):
        return self.client.exists(key, **kwargs)

    def pop(self, **kwargs):
        return self.client.pop(**kwargs)

    def size(self, *args):
        return self.client.size(*args)

if __name__ == '__main__':
    c = DBClient()
    c.changeTable('valid_proxy')
    print(c.size())
    print(c.size('valid_proxy'))
    


