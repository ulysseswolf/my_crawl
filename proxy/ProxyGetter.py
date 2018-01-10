import os
import sys
import re
import requests
from lxml import etree
import redis
from selenium import webdriver
from selenium.webdriver.support.ui import Select

sys.path.append('../')
#from util.functions import robustCrawl
from util.Logger import logger

header = {'Connection': 'keep-alive',
          'Cache-Control': 'max-age=0',
          'Upgrade-Insecure-Requests': '1',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Encoding': 'gzip, deflate, sdch',
          'Accept-Language': 'zh-CN,zh;q=0.8',
         }
RAW_PROXY_QUEUE = 'raw_proxy'
VALID_PROXY_QUEUE = 'valid_proxy'

class ProxyGetter:

    def __init__(self):
        self.db = redis.Redis()

    @staticmethod
    def freeProxy1():
        url = 'http://spys.one/en/anonymous-proxy-list/'
        phantomjs = os.path.abspath(__file__ + '/../../util/phantomjs64')
        driver = webdriver.PhantomJS(phantomjs)
        driver.get(url)
        select = Select(driver.find_element_by_name("xpp"))
        select.select_by_value("4")
        select1 = Select(driver.find_element_by_name("xf1"))
        select1.select_by_value("4")

        l = driver.find_elements_by_css_selector('font.spy14')
        for t in l:
            p = re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', t.text)
            if p:
                yield p.group()


    @staticmethod
    def freeProxy2():
        """
        抓取代理66 http://www.66ip.cn/
        """
        url = "http://www.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=4&start=&ports=&export=&ipaddress=&area=0&proxytype=0&api=66ip"
        # html = request.get(url).content
        # content为未解码，text为解码后的字符串
        html = requests.get(url, headers=header).text
        for proxy in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html):
            yield proxy

    @staticmethod
    def freeProxy3(days=1):
        """
        抓取ip181 http://www.ip181.com/
        :param days:
        """
        url = 'http://www.ip181.com/'
        html = requests.get(url, headers=header).content
        html_tree = etree.HTML(html)
        tr_list = html_tree.xpath('//tr')[1:]
        for tr in tr_list:
            tds = tr.xpath('./td/text()')
            if tds[2] == '高匿':
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy4():
        # 抓取西刺代理
        url_list = ['http://www.xicidaili.com/nn',  # 高匿
                    'http://www.xicidaili.com/nn/2',
                    ]
        for url in url_list:
            html = requests.get(url, headers=header).content
            tree = etree.HTML(html)
            proxy_list = tree.xpath('.//table[@id="ip_list"]//tr')
            for proxy in proxy_list:
                yield ':'.join(proxy.xpath('./td/text()')[0:2])

    @staticmethod
    def _freeProxy5():
        """
        抓取guobanjia http://www.goubanjia.com/free/gngn/index.shtml
        """
        url = "http://www.goubanjia.com/free/gngn/index{page}.shtml"
        for page in range(1, 10):
            page_url = url.format(page=page)
            html = requests.get(page_url, headers=header, timeout=20).content
            tree = etree.HTML(html)
            proxy_list = tree.xpath('//td[@class="ip"]')
            # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
            # 需要过滤掉<p style="display:none;">的内容
            xpath_str = """.//*[not(contains(@style, 'display: none'))
                                and not(contains(@style, 'display:none'))
                                and not(contains(@class, 'port'))
                                ]/text()
                        """
            for each_proxy in proxy_list:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))
                port = each_proxy.xpath(".//span[contains(@class, 'port')]/text()")[0]

                yield '{}:{}'.format(ip_addr, port)

    @staticmethod
    def freeProxy6():
        url = "https://proxy.coderbusy.com/zh-cn/classical/anonymous-type/highanonymous/p%d.aspx"
        for i in range(1,3):
            html = requests.get(url % i, headers=header, timeout=20).content
            tree = etree.HTML(html)
            tr_list = tree.xpath('//tbody//tr')
            for tr in tr_list:
                #print(':'.join(tr.xpath('./td/text()')[0:2]))
                t = tr.xpath('./td/text()')
                yield '{0}:{1}'.format(t[1].strip(), t[2])

    @staticmethod
    def freeProxy7():
        urls = ['http://www.89ip.cn/tiqv.php?sxb=&tqsl=300&ports=&ktip=&xl=on&submit=%CC%E1++%C8%A1']
        for pageurl in urls:
            html = requests.get(pageurl, headers=header, timeout=30).text
            for p in re.findall('\d+\.\d+\.\d+\.\d+:\d+', html):
                yield p

    @staticmethod
    def freeProxy8():
        url = 'http://www.ip181.com/daili/%d.html'
        for i in range(1,4):
            html = requests.get(url % i, headers=header, timeout=30).content
            tree = etree.HTML(html)
            trs = tree.xpath('.//tr')
            for tr in trs:
                tds = tr.xpath('.//td/text()')
                if tds[2] == '高匿':
                    yield '{0}:{1}'.format(tds[0],tds[1])

    @staticmethod
    def freeProxy9():
        urls = ['http://proxy.ipcn.org/proxya.html', 'http://proxy.ipcn.org/proxya2.html',
            'http://proxy.ipcn.org/proxyb.html', 'http://proxy.ipcn.org/proxyb2.html']
        for url in urls:
            html = requests.get(url, headers=header, timeout=30).text
            for p in re.findall('\d+\.\d+\.\d+\.\d+:\d+', html):
                yield p

    @staticmethod
    def freeProxy10():
        url = 'http://www.kxdaili.com/dailiip/1/%d.html'
        for i in range(1,4):
            html = requests.get(url % i, headers=header, timeout=30).text.encode('ISO-8859-1').decode('utf-8', 'ignore')
            tree = etree.HTML(html)
            trs = tree.xpath('//tbody//tr')
            for tr in trs:
                tds = tr.xpath('.//td/text()')
                yield '{0}:{1}'.format(tds[0],tds[1])



    def crawl_proxies(self):
        for m in dir(ProxyGetter):
            crawl_method_r = re.match('freeProxy\d+', m)
            if not crawl_method_r:
                continue
            crawl_method = crawl_method_r.group() 
            logger.info('running %s' % crawl_method)
            # catch generator exceptions 
            try:
                for proxy in getattr(ProxyGetter, crawl_method)():
                    if proxy:
                        # Using LREM and replacing it if it was found.
                        # LREM list 0 "hello", 0 means remove all elements equal to value
                        self.db.lrem(RAW_PROXY_QUEUE, num=0, value=proxy)
                        self.db.lpush(RAW_PROXY_QUEUE, proxy)
                        #logger.info("fetch proxy:{0}, {1}".format(crawl_method, proxy))
            except Exception as e:
                logger.error(e)
                continue


if __name__ == '__main__':
    gg = ProxyGetter()
    #for e in gg.freeProxy1():
    #    print(e)


