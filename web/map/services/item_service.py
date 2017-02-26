import hashlib

from es import es
from datetime import datetime

salt = '7b4dafa43458d3a6a232afdd184ecb53'

es_prod_index = 'object'
es_prod_type = 'item'

es_test_index = 'object_test'
es_test_type = 'item_test'

es_index = es_test_index
es_type = es_test_type


def generate_secret(id):
    return hashlib.md5(id + salt).hexdigest()


def is_valid_secret(id, secret):
    return secret == generate_secret(id)


def generate_id(payload):
    email = payload.get('email')
    address = payload.get('address')
    return hashlib.md5(email + 'peri_map' + address).hexdigest()


def item_exists(id):
    return es.exists(index=es_index, doc_type=es_type, id=id)


def delete_item(id):
    es.delete(index=es_index, doc_type=es_type, id=id)


def search_item(search_body):
    return es.search(index=es_index, doc_type=es_type, body=search_body, filter_path=['hits.hits._*'])


def get_item(id):
    return es.get(index=es_index, doc_type=es_type, id=id)


def items_by_date(date_obj):
    search_body = {
        # "size": 100,
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "updated": {
                                "gte": date_obj.isoformat('T') + 'Z',

                            }
                        }
                    }
                ]
            }
        }
    }
    return search_item(search_body)


def create_item(payload, id=None):
    updated_date = datetime.utcnow().isoformat('T') + 'Z'
    created_date = datetime.utcnow().isoformat('T') + 'Z'
    if id is not None:
        if not item_exists(id):
            raise ValueError('There is no item by this id.')
        created_date = get_item(id).get('creation')
    if id is None:
        id = generate_id(payload)
        if item_exists(id):
            raise ValueError('the combination of email and address already exists.')

    data = {
        'type': payload.get('type'),
        'src': 'peri_map',
        'name': payload.get('name'),
        'creation': created_date,
        'updated': updated_date,
        'detail': {
            'website': payload.get('website'),
            'occupation': payload.get('occupation'),
            'description': payload.get('description'),
            'gender': payload.get('gender'),
            'email': payload.get('email')
        },
        'location': {
            'phone': payload.get('phone'),
            'address': payload.get('address'),
            'geo_set': {
                "lat": payload.get('lat'),
                "lon": payload.get('lon')
            }
        },
    }
    print "data to be indexed \n{}".format(data)
    # store data in elasticsearch
    es.index(index=es_index, doc_type=es_type, id=id, body=data)
    # print "Link to edit: localhost:8001/service/edit?id={}&secret={}".format(id, generate_secret(id))
    return id


def delete_index():
    es.indices.delete(index=es_index)


def create_index():
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

                    },
                    "creation": {
                        "type": "date",
                        "format": "yyyy-MM-dd HH:mm:ss"
                    },
                    "updated": {
                        "type": "date",
                        "format": "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }
        }

    }
    es.indices.create(index=es_index, body=mapping)
