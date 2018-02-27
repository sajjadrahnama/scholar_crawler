#!/bin/bash

while read line; do
    scrapy runspider src/ArticleSpider.py -a max_articles=5000 -a tag="$line"
done < tags.txt
