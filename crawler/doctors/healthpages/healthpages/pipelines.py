# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
from elasticsearch import Elasticsearch


class IndexPipeline(object):
    es = Elasticsearch(['search:9200'], max_retries=50)

    def open_spider(self, spider):
        self.check_mapping()

    def process_item(self, item, spider):
        if spider.name == "healthpages.wiki_detail":
            self.index_item(item)

        return item

    def index_item(self, item):
        item_identity = item["src"] + "{}-{}".format(item["location"]["geo_set"]["lat"],
                                                     item["location"]["geo_set"]["lon"])
        item_id = hashlib.md5(item_identity).hexdigest()
        self.es.index(index='object', doc_type='item', id=item_id, body=item)

    def check_mapping(self):
        self.es.indices.delete(index='object')

        mapping = {
            "settings": {
                "index.number_of_shards": 1,
                "index.number_of_replicas": 1
            },
            "mappings": {
                "item": {
                    "properties": {
                        "location": {
                            "properties": {
                                "geo_set": {
                                    "type": "geo_point"
                                }

                            }

                        }
                    }
                }
            }

        }
        self.es.indices.index(index='object', body=mapping)
