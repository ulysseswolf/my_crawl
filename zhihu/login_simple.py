import requests
import re
import time

def login(user, passwd):
    sess = requests.Session()
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}

    html = sess.get('https://www.zhihu.com/#signin', headers=headers).text
    p = '<input type="hidden" name="_xsrf" value="([0-9a-z]*)"/>'
    xsrf = re.findall(p, html)[0]
    captcha = sess.get('https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time()*1000), headers=headers).content
    data = {'_xsrf': xsrf, 'email': user, 'password': passwd, 'remember_me': True, 'captcha': get_captcha(captcha)}
    sess.post('https://www.zhihu.com/login/email',data,headers=headers)
    resp = sess.get('https://www.zhihu.com', headers=headers)

    print(resp.text)
    print(resp.status_code)

def get_captcha(content):
    with open('cap.gif', 'wb') as f:
        f.write(content)

    return input('input captcha:')

if __name__ == '__main__':
    login('email','passwd',)
