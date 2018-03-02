# In The Name Of God
# ========================================
# [] File Name : conf
#
# [] Creation Date : 28/02/18
#
# [] Created By : Sajjad Rahnama (sajjad.rahnama7@gmail.com)
# =======================================

from bson.objectid import ObjectId
from pymongo import MongoClient

from conf import *


class ArticleModel:
    """Article MongoDB Model"""

    def __init__(self, data):
        self.collection = MongoClient(dbHost, dbPort).scholar.articles
        if type(data) == 'string':
            self.fetch(data)
        else:
            self._id = None
            self.title = data['title']
            self.link = data['link']
            self.authors = data['authors']
            self.abstract = data['abstract']
            self.year = data['year']
            self.citations = data['citations']
            self.citations_link = data['citations_link']
            if 'tag' in data:
                self.tags = {data['tag']: data['index']}
            else:
                self.tags = {}

    def fetch(self, _id):
        document = self.collection.find_one({'_id': ObjectId(_id)})
        if document:
            self.set_data(document)

    def save(self):
        doc = self.existence_check()
        if doc:
            tags = self.tags
            self.set_data(doc)
            self.tags = {**tags, **self.tags}
            self.update()
        else:
            self.insert()

    def set_data(self, data):
        self._id = data['_id']
        self.title = data['title']
        self.link = data['link']
        self.tags = data['tags']
        self.authors = data['authors']
        self.abstract = data['abstract']
        self.year = data['year']
        self.citations = data['citations']
        self.citations_link = data['citations_link']

    def update(self):
        result = self.collection.update_one({'_id': ObjectId(self._id)}, {"$set": {
            'title': self.title,
            'link': self.link,
            'tags': self.tags,
            'authors': self.authors,
            'abstract': self.abstract,
            'year': self.year,
            'citations': self.citations,
            'citations_link': self.citations_link,
        }}, upsert=False)
        print(result.matched_count)

    def insert(self):
        self._id = self.collection.insert_one({
            'title': self.title,
            'link': self.link,
            'tags': self.tags,
            'authors': self.authors,
            'abstract': self.abstract,
            'year': self.year,
            'citations': self.citations,
            'citations_link': self.citations_link,
        }).inserted_id

    def existence_check(self):
        document = self.collection.find_one(
            {'title': self.title, 'authors': self.authors}
        )
        return document

    @property
    def id(self):
        return self._id
