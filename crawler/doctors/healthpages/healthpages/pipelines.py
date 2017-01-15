# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import requests
from requests.packages.urllib3.util.retry import Retry

class IndexPipeline(object):
    index_link = "http://search:9200/object/item/{}"
    mapping_link = "http://search:9200/object"
    session = requests.Session()
    retries = Retry(total=50,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 501, 502, 503, 504 ])

    def open_spider(self, spider):
        self.check_mapping()

        a = requests.adapters.HTTPAdapter(max_retries=self.retries)
        self.session.mount('http://', a)

    def process_item(self, item, spider):
        if spider.name == "healthpages.wiki_detail":
            self.index_item(item)

        return item

    def index_item(self, item):
        item_identity = item["src"] + "{}-{}".format(item["location"]["geo_set"]["lat"],
                                                     item["location"]["geo_set"]["lon"])
        id_hash = hashlib.md5(item_identity).hexdigest()
        self.session.post(self.index_link.format(id_hash), json=item)

    def check_mapping(self):
        self.session.delete(self.mapping_link)

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
        self.session.put(self.mapping_link, json=mapping)
