import hashlib
from django.http import HttpResponse

from es import es
from . import recaptcha

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


def check_recaptcha(recaptcha_value):
    recaptcha_success = recaptcha.check(recaptcha_value)

    if not recaptcha_success:
        return HttpResponse('invalid Recaptcha.', status=401)
    return None


def check_secret(payload):
    if not is_valid_secret(payload.get('id'), payload.get('secret')):
        return HttpResponse('You are not allowed to this operation.', status=401)
    return None


def edit_item(payload):
    id = payload.get('id')
    return create_item(payload, id)


def delete_item(payload):
    # check the secret
    id = payload.get('id')
    es.delete(index='object', doc_type='item', id=id)
    return HttpResponse()


def create_item(payload, id=None):
    if id is None:
        id = generate_id(payload)

    if not item_exists(id):
        return HttpResponse('the email address already exists.', status=401)

    data = {
        'type': payload.get('category'),
        'src': 'peri_map',
        'name': payload.get('name'),
        'detail': {
            'website': payload.get('link'),
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
    res = es.index(index='object', doc_type='item', id=id, body=data)
    # todo check response of the res

    return HttpResponse()
