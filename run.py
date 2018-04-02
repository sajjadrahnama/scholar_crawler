from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from src.main_spider import MainSpider
from src.citation_spider import CitationSpider
from src.conf import next_topic


def run(topic, index):
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    # importing project settings for further usage
    # mainly because of the middlewares
    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    # running spiders sequentially (non-distributed)
    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(MainSpider, topic=topic, index=index)
        reactor.stop()

    crawl()
    reactor.run()


topic = next_topic()
while topic:
    run(topic['topic'], topic['index'])
    topic = next_topic()
