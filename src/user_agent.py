import random
from xml.dom import minidom
from scrapy.utils.project import get_project_settings


class RandomUserAgent(object):
    settings = get_project_settings()
    source_path = 'src/data/user_agents.xml'

    def __init__(self):
        xmldoc = minidom.parse(self.source_path)
        items = xmldoc.getElementsByTagName('useragent')
        self.user_agents = [item.attributes['value'].value for item in items]

    def set_header(self, request):
        user_agent = random.choice(self.user_agents)
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)
        return request
