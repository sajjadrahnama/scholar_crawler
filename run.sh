#!/bin/bash

while read line; do
    echo "Crawling $line"
    scrapy runspider src/main_spider.py -a tag="$line"
done < tags.txt

#-s LOG_ENABLED=False
