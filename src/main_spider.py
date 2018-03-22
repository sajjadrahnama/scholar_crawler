import scrapy
import re
import logging
import time
from pymongo import MongoClient
from conf import *
from article_model import ArticleModel


class MainSpider(scrapy.Spider):
    handle_httpstatus_list = [403, 503, 302, 31]
    dont_redirect = True
    name = "main"

    def __init__(self, topic):
        logging.getLogger('scrapy').setLevel(logging.ERROR)
        self.start = 0
        self.topic = topic
        super().__init__()

    def start_requests(self):
        base_url = "https://scholar.google.com/scholar?as_vis=1&as_sdt=1,5&q={}&hl=en&start=0"
        url = base_url.format(re.sub(' ', '+', self.topic))
        insert_topic(self.topic)
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        log(response)
        i = 1
        scholar_url = 'https://scholar.google.com'
        for obj in response.css('.gs_r.gs_or.gs_scl .gs_ri'):
            authors, year = extract_authors(obj.css('.gs_a').xpath('string(.)').extract_first())
            data = {
                'title': obj.css('.gs_rt a').xpath('string(.)').extract_first(),
                'link': obj.css('.gs_rt a::attr(href)').extract_first(),
                'topic': self.topic,
                'index': self.start + i,
                'authors': authors,
                'year': year,
                'abstract': obj.css('.gs_rs').xpath('string(.)').extract_first(),
                'citations': int(re.search('(\d+)', obj.css('.gs_fl').xpath('string(a[3])').extract_first()).group(1)),
                'citations_link': scholar_url + obj.css('.gs_fl').xpath('a[3]/@href').extract_first() + '&as_vis=1',
                'citations_flag': False,
            }
            model = ArticleModel(data)
            model.save()
            i += 1
        self.start += 10
        next_page = re.sub('start=[0-9]*$', 'start=' + str(self.start), response.url)

        if self.start < maxArticle:
            yield response.follow(next_page, callback=self.parse)


def extract_authors(raw):
    year = int(re.search('-.*(\d{4})', raw).group(1))
    raw = re.sub('….*', '', raw)
    raw = re.sub('\xa0', ' ', raw)
    raw = re.sub(' - .*', '', raw)
    raw = re.split('\s*,\s*', raw)
    return raw, year


def insert_topic(topic):
    collection = MongoClient(dbHost, dbPort).scholar.topics
    existed_topic = collection.find_one({'topic': topic})
    if not existed_topic:
        collection.insert_one({'topic': topic})


def log(response):
    res = re.findall('q=([\w+]*).*start=([\d]+)', response.url)
    topic = res[0][0].replace('+', ' ')
    start = res[0][1]
    res = str(response.status) + '\t'
    res += time.strftime("%m-%d %H:%M:%S", time.localtime()) + '\t'
    res += start + '\t'
    res += topic + '\n'
    with open("logs/main.txt", "a") as file:
        file.write(res)
