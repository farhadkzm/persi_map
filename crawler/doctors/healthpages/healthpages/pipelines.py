# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import requests


class IndexPipeline(object):
    index_link = "http://search:9200/object/item/{}"
    mapping_link = "http://search:9200/object"

    def open_spider(self, spider):
        self.check_mapping()

    def process_item(self, item, spider):
        if spider.name == "healthpages.wiki_detail":
            self.index_item(item)
            return item
        return item

    def index_item(self, item):
        item_identity = item['type'] % item['src']
        id_hash = hashlib.md5(item_identity).hexdigest()
        requests.post(self.index_link.format(id_hash), json=item)

    def check_mapping(self):
        requests.delete(self.mapping_link)

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
        requests.put(self.mapping_link, json=mapping)

