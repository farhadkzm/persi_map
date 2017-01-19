# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
from elasticsearch import Elasticsearch
from elasticsearch import TransportError
from elasticsearch import ConnectionError
from time import sleep

class IndexPipeline(object):
    es = Elasticsearch(['search:9200'],retries=True, max_retries=10, retry_on_timeout=True, dead_timeout=2)

    def open_spider(self, spider):
        self.check_mapping(5000)

    def process_item(self, item, spider):
        if spider.name == "healthpages.wiki_detail":
            self.index_item(item)

        return item

    def index_item(self, item):
        item_identity = item["src"] + "{}-{}".format(item["location"]["geo_set"]["lat"],
                                                     item["location"]["geo_set"]["lon"])
        item_id = hashlib.md5(item_identity).hexdigest()
        self.es.index(index='object', doc_type='item', id=item_id, body=item)

    def check_mapping(self, retry):
        try:
            self.es.indices.delete(index='object')
        except ConnectionError:
            if retry > 1:
                print 'Sleeping for 5 seconds.'
                sleep(5)
                self.check_mapping(retry -1)
            return
        except TransportError as err:
            if err.status_code == 404:
                print 'Index has not been created yet. Now trying to create a new one...'
            else:
                raise

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
        self.es.indices.create(index='object', body=mapping)
