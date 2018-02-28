import scrapy
import re
import logging
from article_model import ArticleModel


class MainSpider(scrapy.Spider):
    name = "main"

    def __init__(self, tag):
        logging.getLogger('scrapy').setLevel(logging.ERROR)
        self.start = 0
        # self.max_articles = max_articles
        self.max_articles = 0
        self.tag = tag
        super().__init__()

    def start_requests(self):
        base_url = "https://scholar.google.com/scholar?as_vis=1&as_sdt=1,5&q={}&hl=en&start=0"
        url = base_url.format(re.sub(' ', '+', self.tag))
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        i = 1
        scholar_url = 'https://scholar.google.com'
        for obj in response.css('.gs_r.gs_or.gs_scl .gs_ri'):
            data = {
                'title': obj.css('.gs_rt a').xpath('string(.)').extract_first(),
                'tag': self.tag,
                'index': self.start + i,
                'authors': authors(obj.css('.gs_a').xpath('string(.)').extract_first()),
                'abstract': obj.css('.gs_rs').xpath('string(.)').extract_first(),
                'citations': int(re.search('(\d+)', obj.css('.gs_fl').xpath('string(a[3])').extract_first()).group(1)),
                'citations_link': scholar_url + obj.css('.gs_fl').xpath('a[3]/@href').extract_first() + '&as_vis=1',
            }
            model = ArticleModel(data)
            model.save()
            i += 1
            return
        self.start += 10
        next_page = re.sub('start=[0-9]*$', 'start=' + str(self.start), response.url)

        if self.start < self.max_articles:
            yield response.follow(next_page, callback=self.parse)


def authors(raw):
    raw = re.sub('….*', '', raw)
    raw = re.sub('\xa0', ' ', raw)
    raw = re.sub(' - .*', '', raw)
    raw = re.split('\s*,\s*', raw)
    return raw
