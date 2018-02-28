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
        self.start = 0
        self.max_articles = 0
        super().__init__()

    def start_requests(self):
        collection = MongoClient(dbHost, dbPort).scholar.articles
        while True:
            pass

    def parse(self, response):
        pass