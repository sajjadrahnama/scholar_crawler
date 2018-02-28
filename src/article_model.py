# In The Name Of God
# ========================================
# [] File Name : conf
#
# [] Creation Date : 28/02/18
#
# [] Created By : Sajjad Rahnama (sajjad.rahnama7@gmail.com)
# =======================================

from pymongo import MongoClient
from bson.objectid import ObjectId
from conf import *


class ArticleModel:
    """Article MongoDB Model"""

    def __init__(self, data):
        self.collection = MongoClient(dbHost, dbPort).scholar.articles
        if type(data) == 'string':
            self.fetch(data)
            print(data)
        else:
            self._id = None
            self.title = data['title']
            self.tags = {data['tag']: data['index']}
            self.authors = data['authors']
            self.abstract = data['abstract']
            self.citations = data['citations']
            self.citations_link = data['citations_link']

    def fetch(self, _id):
        document = self.collection.find_one({'_id': ObjectId(_id)})
        if document:
            self.set_data(document)

    def save(self):
        doc = self.existence_check()
        if doc:
            self.tags = {**doc['tags'], **self.tags}
            self.update()
        else:
            self.insert()

    def set_data(self, data):
        self._id = data['_id']
        self.title = data['title']
        self.tags = data['tags']
        self.authors = data['authors']
        self.abstract = data['abstract']
        self.citations = data['citations']
        self.citations_link = data['citations_link']

    def update(self):
        self.collection.update_one({'_id': self._id}, {"$set": {
            'title': self.title,
            'tags': self.tags,
            'authors': self.authors,
            'abstract': self.abstract,
            'citations': self.citations,
            'citations_link': self.citations_link,
        }}, upsert=False)

    def insert(self):
        self._id = self.collection.insert_one({
            'title': self.title,
            'tags': self.tags,
            'authors': self.authors,
            'abstract': self.abstract,
            'citations': self.citations,
            'citations_link': self.citations_link,
        }).inserted_id

    def existence_check(self):
        document = self.collection.find_one(
            {'title': self.title, 'authors': self.authors}
        )
        return document
