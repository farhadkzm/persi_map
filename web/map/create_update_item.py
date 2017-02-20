from . import recaptcha
import requests


def handle_new_item_post(request):
    payload = json.loads(request.body)

    recaptcha_success = recaptcha.check_recaptcha(payload)

    if not recaptcha_success:
        return HttpResponse(status=401)

    if not send_email(payload):
        return HttpResponse(status=401)

    email = cleanhtml(payload.get('email'))
    id = hashlib.md5(email).hexdigest()
    if not item_exists(id):
        return HttpResponse(status=401)

    data = {
        'type': cleanhtml(payload.get('category')),
        'src': 'peri_map',
        'name': cleanhtml(payload.get('name')),
        'detail': {
            'website': cleanhtml(payload.get('link')),
            'occupation': cleanhtml(payload.get('occupation')),
            'description': cleanhtml(payload.get('description')),
            'gender': cleanhtml(payload.get('gender')),
            'email': email
        },
        'location': {
            'phone': cleanhtml(payload.get('phone')),
            'address': cleanhtml(payload.get('address')),
            'geo_set': {
                "lat": cleanhtml(payload.get('lat')),
                "lon": cleanhtml(payload.get('lon'))
            }
        },
    }
    # store data in elasticsearch
    res = es.index(index='object', doc_type='item', id=id, body=data)
    # todo check response of the res

    return HttpResponse()
