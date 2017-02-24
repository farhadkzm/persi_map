import hashlib

from es import es

salt = '7b4dafa43458d3a6a232afdd184ecb53'


def generate_secret(id):
    return hashlib.md5(id + salt).hexdigest()


def is_valid_secret(id, secret):
    return secret == generate_secret(id)


def generate_id(payload):
    email = payload.get('email')
    address = payload.get('address')
    return hashlib.md5(email + 'peri_map' + address).hexdigest()


def item_exists(id):
    return es.exists(index='object', doc_type='item', id=id)


def delete_item(id):
    es.delete(index='object', doc_type='item', id=id)


def create_item(payload, id=None):
    if id is not None and not item_exists(id):
        raise ValueError('There is no item by this id.')

    if id is None:
        id = generate_id(payload)
        if item_exists(id):
            raise ValueError('the combination of email and address already exists.')

    data = {
        'type': payload.get('type'),
        'src': 'peri_map',
        'name': payload.get('name'),
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
    # store data in elasticsearch
    es.index(index='object', doc_type='item', id=id, body=data)
    print "Link to edit: localhost:8001/service/edit?id={}&secret={}".format(id, generate_secret(id))
    return id


def delete_index():
    es.indices.delete(index='object')


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

                    }
                }
            }
        }

    }
    es.indices.create(index='object', body=mapping)
