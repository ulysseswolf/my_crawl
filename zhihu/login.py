import requests
import time
import re
import os
import json
import random
import sys
#import subprocess
sys.path.append('../')
from util.user_agents import agents
from util.Logger import logger

signURL = 'https://www.zhihu.com/#signin'
loginURL = 'https://www.zhihu.com/login/email'
mainPageURL = 'https://www.zhihu.com'
captchaURL = 'https://www.zhihu.com/captcha.gif?r=%d&type=login'
authTestURL = 'https://www.zhihu.com/api/v4/members/xzer/followers?offset=0&limit=20'

# 用户账号登陆模块
class AccountManager:
    __slots__ = ('email', 'password', 'cookie', 'session')

    requestHeader = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                 #"Accept-Encoding": "gzip, deflate, br",
                 #"Accept-Language": "en-US,en;q=0.9,zh;q=0.8",
                 "Host": "www.zhihu.com",
                 "Origin": "https://www.zhihu.com",
                 "Referer": "https://www.zhihu.com/",
                 "Upgrade-Insecure-Requests": "1",
                 "User-Agent": random.choice(agents)
                 }

    captchaFile = os.path.join(sys.path[0], 'captcha.gif')
    cookieFile = os.path.join(sys.path[0], 'cookie')
    def __init__(self, email=None, password=None):
        # 设置脚本所在目录为当前工作目录
        os.chdir(sys.path[0])

        self.session = requests.Session()
        self.session.headers = self.requestHeader

        # 普通登陆信息
        self.email = email
        self.password = password

        #self.cookie = self.load_cookie()
        self.cookie = None

    # 返回登陆凭证
    def get_auth_token(self):
        return self.cookie

    def load_cookie(self):
        """
        读取cookie文件，返回反序列化后的dict对象，
        没有则返回None
        Cookie有过期时间的，如果代码没有正确获取到数据，报302之类的错误一般可能Cookie失效了
        """

        if os.path.exists(self.cookieFile):
            with open(self.cookieFile, 'r') as f:
                cookie = json.load(f)
                return cookie
        return None

    def login(self):
        if self.cookie:
            logger.info("检测到cookie文件，直接使用cookie登录")
            self.cookie_login()
        else:
            logger.info("使用email登录")
            self.common_login()

    # Cookie 登陆方式
    def cookie_login(self):
        # 获取基本的cookie
        self.session.get(mainPageURL)

        # 添加用户配置的认证Cookie
        cookie = self.load_cookie()
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookie)

        # 检验是否成功登陆
        response = self.session.get(authTestURL)
        
        if response.status_code == 200:
            logger.info('知乎账户登陆成功')
            return True
        else:
            logger.info('知乎账户登陆失败')
            logger.info(response.text)
            return False

    # 普通登陆方式
    def common_login(self):
        try:
            response = self.session.get(signURL).content.decode('utf-8')
            # 获取 _xsrf
            xsrf_p = '<input type="hidden" name="_xsrf" value="([0-9a-z]*)"/>'
            result = re.search(xsrf_p, response)
            if result:
                _xsrf = result.group(1)
            else:
                logger.info('xsrf not found')
                return False
            
            captcha = self.session.get(captchaURL % (time.time()*1000)).content
            with open(self.captchaFile, 'wb') as output:
                output.write(captcha)

            #subprocess.call(self.captchaFile, shell=True)
            captcha = input('input captcha:')
            
            # login
            form_data = {'_xsrf': _xsrf,
                         'email': self.email,
                         'password': self.password,
                         'remember_me': True,
                         'captcha': captcha}
            self.requestHeader.update({'X-Requested-With': 'XMLHttpRequest', 'X-Xsrftoken': _xsrf})
            self.session.headers = self.requestHeader
            response = self.session.post(url=loginURL, data=form_data)
            if response.status_code == 200:
                logger.info(response.text)
                # 检查是否已经登陆成功
                response = self.session.get(authTestURL)
                if response.status_code == 200:
                    # 保存登陆认证cookie
                    self.cookie = self.session.cookies.get_dict()
                    logger.info('知乎账户登陆成功')
                    os.remove(self.captchaFile)

                    with open(self.cookieFile, 'w') as output:
                        cookies = self.session.cookies.get_dict()
                        json.dump(cookies, output)
                        logger.info("已在同目录下生成cookie文件")

        except Exception as e:
            logger.info('知乎账户登陆失败')
            logger.error(e)
        finally:
            self.session.close()
            logger.info('session closed')

    def dump_cookie(self):
        self.session.get('https://www.zhihu.com/topic/19550994/top-answers', headers=self.requestHeader)
        c = self.session.cookies.get_dict()
        with open(self.cookieFile, 'w') as output:
            json.dump(c, output)



if __name__ == '__main__':
    account_manager = AccountManager(email='', password='')
    account_manager.login()
    #print(account_manager.get_auth_token())
    account_manager.dump_cookie()
