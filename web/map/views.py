import json
import re
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader

from services.item_service import *
from services.recaptcha import check_recaptcha


def api_search(request):
    geo_distance = {
        "distance": request.GET.get('distance', ''),
        "location.geo_set": {
            "lat": float(request.GET.get('lat', 0)),
            "lon": float(request.GET.get('lng', 0))
        }
    }

    category = request.GET.get('type', '')
    name = request.GET.get('name', '')
    occupation = request.GET.get('occupation', '')
    clinic = request.GET.get('clinic', '')
    gender = request.GET.get('gender', '')

    must_blocks = [{
        "geo_distance": geo_distance
    }]

    if name != '':
        must_blocks.append({
            "wildcard": {
                "name": "*{}*".format(name)
            }
        })

    if occupation != '':
        must_blocks.append({
            "match": {
                "detail.occupation": occupation
            }
        })

    if clinic != '':
        must_blocks.append({
            "wildcard": {
                "location.clinic_name": "*{}*".format(clinic)
            }
        })

    if gender != '':
        must_blocks.append({
            "match": {
                "detail.gender": gender
            }
        })

    search_body = {
        "size": 100,
        "query": {
            "bool": {
                "must": must_blocks,
                "filter": [
                    {
                        "term": {
                            "type": category
                        }
                    }
                ]
            }
        }
    }

    print "Search request to be sent to ES\n{}".format(search_body)
    result = es.search(index='object', doc_type='item', body=search_body, filter_path=['hits.hits._*'])
    return JsonResponse(result)


def index(request):
    template = loader.get_template('map/index.html')
    return HttpResponse(template.render({}, request))


def new_service(request):
    return render(request, "map/item.html", {'item': 'undefined', 'secret': 'undefined'})


def edit_service(request):
    if request.method != 'GET':
        return HttpResponse("Invalid dd address", status=404)

    id = request.GET.get('id', None)
    secret = request.GET.get('secret', None)

    if id is None or secret is None or not is_valid_secret(id, secret):
        return HttpResponse("Invalid id or url is corrupted", status=412)

    item = es.get(index='object', doc_type='item', id=id)
    return render(request, "map/item.html", {'item': json.dumps(item), 'secret': secret})


def api_delete_item(request):
    payload = json.loads(request.body)
    id = payload.get('id')
    secret = payload.get('secret')
    recaptcha = payload.get('recaptcha')
    if id is None \
            or secret is None \
            or not is_valid_secret(id, secret) \
            or not check_recaptcha(recaptcha):
        return HttpResponse(status=401)
    delete_item(id)
    return HttpResponse()


def api_create_update_item(request):
    payload = json.loads(request.body)
    id = payload.get('id')
    secret = payload.get('secret')
    recaptcha = payload.get('recaptcha')

    if not check_recaptcha(recaptcha):
        return HttpResponse(status=401)

    if id is not None:  # operation is UPDATE
        if secret is None \
                or not is_valid_secret(id, secret):
            return HttpResponse(status=401)

    try:
        id = create_item(payload, id)
        return JsonResponse({'link': "/service/edit?id={}&secret={}".format(id, generate_secret(id))})
    except ValueError as e:
        return HttpResponse(e, status=401)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext
