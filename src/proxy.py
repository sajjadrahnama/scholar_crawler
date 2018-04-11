import random
import requests
from bs4 import BeautifulSoup


class HttpProxy(object):
    proxies = []
    max_proxies = 100
    url = 'https://www.proxydocker.com/en/proxylist/search?port=All&type=HTTP&anonymity=All&country=All&city=All&state=All&need=Google'

    def __init__(self):
        self.query_proxies()

    def query_proxies(self):
        request = requests.post(self.url, data={'page': random.randrange(0, 7)})
        response = request.text
        if request.status_code == 200:
            i = 0
            soup = BeautifulSoup(response, 'html.parser')
            for row in soup.find_all('tr'):
                cells = row.findAll('td')
                if len(cells) > 2:
                    self.proxies.append({
                        'address': cells[0].text.strip(),
                        'protocol': cells[1].text.lower().strip()
                    })
                    i += 1
                    if i == self.max_proxies:
                        break

    def proxy(self):
        try:
            temp = random.choice(self.proxies)
        except Exception:
            return  None
        return temp


