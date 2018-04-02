import scrapy
import re
import logging
import time
from src.conf import db_client, maxArticle, productionMode, save_topic
from src.article_model import ArticleModel
from src.tor import change_ip
from src.user_agent import RandomUserAgent
from src.proxy import HttpProxy


class MainSpider(scrapy.Spider):
    handle_httpstatus_list = [403, 503, 302, 31]
    dont_redirect = True
    name = "main"

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'COOKIES_ENABLED': False
    }

    def __init__(self, topic, index):
        logging.getLogger('scrapy').setLevel(logging.ERROR)
        self.start = index
        self.topic = topic
        self.user_agents = RandomUserAgent()
        self.proxy_factory = HttpProxy()
        self.proxy = None
        super().__init__()

    def start_requests(self):
        base_url = "https://scholar.google.com/scholar?as_vis=1&as_sdt=1,5&q={}&hl=en&start=" + str(self.start)
        url = base_url.format(re.sub(' ', '+', self.topic))
        req = scrapy.Request(url=url, callback=self.parse)
        self.user_agents.set_header(req)
        self.set_proxy(req)
        if self.start < maxArticle:
            yield req

    def parse(self, response):
        log(response)
        i = 1
        scholar_url = 'https://scholar.google.com'
        for obj in response.css('.gs_r.gs_or.gs_scl .gs_ri'):
            try:
                authors, year = extract_authors(obj.css('.gs_a').xpath('string(.)').extract_first())
                citations = re.search('(\d+)', obj.css('.gs_fl').xpath('string(a[3])').extract_first())
                if citations:
                    citations = int(citations.group(1))
                data = {
                    'title': obj.css('.gs_rt a').xpath('string(.)').extract_first(),
                    'link': obj.css('.gs_rt a::attr(href)').extract_first(),
                    'topic': self.topic,
                    'index': self.start + i,
                    'authors': authors,
                    'year': year,
                    'abstract': obj.css('.gs_rs').xpath('string(.)').extract_first(),
                    'citations': citations,
                    'citations_link': scholar_url + obj.css('.gs_fl').xpath('a[3]/@href').extract_first() + '&as_vis=1',
                    'citations_index': 0,
                }
                model = ArticleModel(data)
                model.save()
                i += 1
            except Exception:
                log(response, i)
        if not response.css('.gs_r.gs_or.gs_scl .gs_ri'):
            log(response, -400)
            print('400\t User Agent:  ' + str(response.request.headers['User-Agent']))
            self.proxy = self.proxy_factory.proxy()
            print('new proxy: ' + str(self.proxy.address))
        else:
            save_topic(self.topic, self.start + 10)
            print('200\t User Agent:  ' + str(response.request.headers['User-Agent']))
            self.start += 10

        # if self.start % 250 == 0 and productionMode:
        #     change_ip()
        next_page = re.sub('start=[0-9]*$', 'start=' + str(self.start), response.url)

        if self.start < maxArticle:
            req = scrapy.Request(url=next_page, callback=self.parse)
            req = self.user_agents.set_header(req)
            yield req

    def set_proxy(self, req):
        if self.proxy:
            req.meta['proxy'] = self.proxy.address


def extract_authors(raw):
    year = int(re.search('-.*(\d{4})', raw).group(1))
    raw = re.sub('….*', '', raw)
    raw = re.sub('\xa0', ' ', raw)
    raw = re.sub(' - .*', '', raw)
    raw = re.split('\s*,\s*', raw)
    return raw, year


def log(response, error=-1):
    res = re.findall('q=([\w+]*).*start=([\d]+)', response.url)
    topic = res[0][0].replace('+', ' ')
    start = res[0][1]
    res = str(response.status) + '\t'
    res += time.strftime("%m-%d %H:%M:%S", time.localtime()) + '\t'
    res += start + '\t'
    res += topic + '\n'
    if error != -1:
        res = 'ERROR\t' + str(error) + '\n' + res + '\n'
    with open("logs/main.txt", "a") as file:
        file.write(res)
