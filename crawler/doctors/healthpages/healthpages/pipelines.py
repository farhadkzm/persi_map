# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
from elasticsearch import Elasticsearch


class IndexPipeline(object):
    es = Elasticsearch([{
        'host': 'search-persi-es-4zjjaw2exoo73nq2xbq3mvulie.us-west-2.es.amazonaws.com', 'port': 443, 'use_ssl': True
    }])

    def process_item(self, item, spider):
        if spider.name == "healthpages.wiki_detail":
            self.index_item(item)

        return item

    def index_item(self, item):
        item_identity = "{}-{}-{}".format(item["src"],
                                          item["location"]["geo_set"]["lat"],
                                          item["location"]["geo_set"]["lon"])
        id = hashlib.md5(item_identity).hexdigest()
        self.es.index(index='object', doc_type='item', id=id, body=item)
