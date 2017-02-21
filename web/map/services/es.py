from elasticsearch import Elasticsearch

es = Elasticsearch([{
    'host': 'search-persi-es-4zjjaw2exoo73nq2xbq3mvulie.us-west-2.es.amazonaws.com', 'port': 443, 'use_ssl': True
}])
