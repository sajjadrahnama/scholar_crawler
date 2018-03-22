import scrapy
import re
import logging
import time
from conf import *
from pymongo import MongoClient
from article_model import ArticleModel


class CitationSpider(scrapy.Spider):
    handle_httpstatus_list = [403, 503, 302, 31]
    dont_redirect = True
    name = "citation"

    def __init__(self):
        logging.getLogger('scrapy').setLevel(logging.ERROR)
        self.collection = MongoClient(dbHost, dbPort).scholar.citaions
        super().__init__()

    def start_requests(self):
        collection = MongoClient(dbHost, dbPort).scholar.articles
        cursor = collection.find({'citations_flag': False})
        for article in cursor:
            yield scrapy.Request(url=article['citations_link'] + 'start=0', callback=self.parse,
                                 meta={'article': article})
            collection.update_one({'_id': article['_id']}, {"$set": {
                'citations_flag': True
            }})

    def parse(self, response):
        log(response)
        scholar_url = 'https://scholar.google.com'
        for obj in response.css('.gs_r.gs_or.gs_scl .gs_ri'):
            authors, year = extract_authors(obj.css('.gs_a').xpath('string(.)').extract_first())
            data = {
                'title': obj.css('.gs_rt a').xpath('string(.)').extract_first(),
                'link': obj.css('.gs_rt a::attr(href)').extract_first(),
                'authors': authors,
                'year': year,
                'abstract': obj.css('.gs_rs').xpath('string(.)').extract_first(),
                'citations': int(re.search('(\d+)', obj.css('.gs_fl').xpath('string(a[3])').extract_first()).group(1)),
                'citations_link': scholar_url + obj.css('.gs_fl').xpath('a[3]/@href').extract_first() + '&as_vis=1',
                'citations_flag': True,
            }
            model = ArticleModel(data)
            model.save()
            self.cite(model.id, response.meta['article']['_id'])
        start = int(re.findall('start=([\d]+)', response.url)[0]) + 10
        next_page = re.sub('start=[0-9]*$', 'start=' + str(start), response.url)

        if start < maxCArtcile:
            yield response.follow(next_page, callback=self.parse, meta=response.meta)

    def cite(self, source, dest):
        self.collection.insert_one({
            'source': source,
            'dest': dest,
        })


def extract_authors(raw):
    year = int(re.search('-.*(\d{4})', raw).group(1))
    raw = re.sub('….*', '', raw)
    raw = re.sub('\xa0', ' ', raw)
    raw = re.sub(' - .*', '', raw)
    raw = re.split('\s*,\s*', raw)
    return raw, year


def log(response):
    res = re.findall('start=([\d]+)', response.url)
    start = res[0]
    res = str(response.status) + '\t'
    res += time.strftime("%m-%d %H:%M:%S", time.localtime()) + '\t'
    res += start + '\t'
    res += str(response.meta['article']['_id']) + '\n'
    with open("logs/citation.txt", "a") as file:
        file.write(res)
