import scrapy
import re
import logging
from conf import *
from pymongo import MongoClient
from article_model import ArticleModel


class CitationSpider(scrapy.Spider):
    name = "citation"

    def __init__(self):
        logging.getLogger('scrapy').setLevel(logging.ERROR)
        self.collection = MongoClient(dbHost, dbPort).scholar.citaions
        self.start = 0
        self.max_articles = 0
        super().__init__()

    def start_requests(self):
        collection = MongoClient(dbHost, dbPort).scholar.articles
        cursor = collection.find({'citation_flag': {'$exists': False}})
        for article in cursor:
            yield scrapy.Request(url=article['citations_link'], callback=self.parse, meta={'article': article})
            collection.update_one({'_id': article['_id']}, {"$set": {
                'citation_flag': True
            }})

    def parse(self, response):
        scholar_url = 'https://scholar.google.com'
        for obj in response.css('.gs_r.gs_or.gs_scl .gs_ri'):
            pass
            authors, year = extract_authors(obj.css('.gs_a').xpath('string(.)').extract_first())
            data = {
                'title': obj.css('.gs_rt a').xpath('string(.)').extract_first(),
                'link': obj.css('.gs_rt a::attr(href)').extract_first(),
                'authors': authors,
                'year': year,
                'abstract': obj.css('.gs_rs').xpath('string(.)').extract_first(),
                'citations': int(re.search('(\d+)', obj.css('.gs_fl').xpath('string(a[3])').extract_first()).group(1)),
                'citations_link': scholar_url + obj.css('.gs_fl').xpath('a[3]/@href').extract_first() + '&as_vis=1',
            }
            model = ArticleModel(data)
            model.save()
            self.cite(model.id, response.meta['article']['_id'])
        self.start += 10
        next_page = re.sub('start=[0-9]*$', 'start=' + str(self.start), response.url)

        if self.start < self.max_articles:
            yield response.follow(next_page, callback=self.parse)

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
