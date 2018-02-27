import scrapy
import re
import json


class ArticleSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, max_articles, tag):
        super().__init__()
        self.start = 0
        # self.max_articles = max_articles
        self.max_articles = 0
        self.tag = tag

    def start_requests(self):
        base_url = "https://scholar.google.com/scholar?as_vis=1&as_sdt=1,5&q={}&hl=en&start=0"
        url = base_url.format(re.sub(' ', '+', self.tag))
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        i = 1
        scholar_base_url = 'https://scholar.google.com'
        for obj in response.css('.gs_r.gs_or.gs_scl .gs_ri'):
            art = Article(
                title=obj.css('.gs_rt a').xpath('string(.)').extract_first(),
                tag=self.tag,
                index=self.start + i,
                authors=authors(obj.css('.gs_a').xpath('string(.)').extract_first()),
                abstract=obj.css('.gs_rs').xpath('string(.)').extract_first(),
                citations=int(re.search('(\d+)', obj.css('.gs_fl').xpath('string(a[3])').extract_first()).group(1)),
                citations_link=scholar_base_url + obj.css('.gs_fl').xpath('a[3]/@href').extract_first() + '&as_vis=1',
            )
            i += 1
        self.start += 10
        next_page = re.sub('start=[0-9]*$', 'start=' + str(self.start), response.url)

        if self.start < self.max_articles:
            yield response.follow(next_page, callback=self.parse)


class Article(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    tag = scrapy.Field()
    index = scrapy.Field()
    authors = scrapy.Field()
    abstract = scrapy.Field()
    citations = scrapy.Field()
    citations_link = scrapy.Field()


def authors(raw):
    raw = re.sub('….*', '', raw)
    raw = re.sub('\xa0', ' ', raw)
    raw = re.sub(' - .*', '', raw)
    raw = re.split('\s*,\s*', raw)
    return raw
