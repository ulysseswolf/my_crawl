import os
from configparser import ConfigParser
import sys
sys.path.append('../')
from util.classes import LazyProperty

class Config:
    def __init__(self):
        pwd = os.path.split(os.path.realpath(__file__))[0]
        self.config = ConfigParser()
        self.config.read(os.path.join(os.path.split(pwd)[0], 'config.ini'))

    def get(self, group, key):
        return self.config.get(group, key)
    
    @LazyProperty
    def db_type(self):
        return self.config.get('DB', 'type')

    @LazyProperty
    def db_host(self):
        return self.config.get('DB', 'host')

    @LazyProperty
    def db_port(self):
        return self.config.get('DB', 'port')

    @LazyProperty
    def db_name(self):
        return self.config.get('DB', 'name')

    
if __name__ == '__main__':
    c = Config()
    print(c.get('DB', 'host'))
    print(c.db_type)

