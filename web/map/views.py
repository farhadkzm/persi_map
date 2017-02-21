import json
import re
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader

from create_update_item import *


def search(request):
    geo_distance = {
        "distance": request.GET.get('distance', ''),
        "location.geo_set": {
            "lat": float(request.GET.get('lat', 0)),
            "lon": float(request.GET.get('lng', 0))
        }
    }

    category = request.GET.get('category', '')
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


def edit_item(request):
    id = None
    secret = None

    if request.method == 'GET':
        id = request.GET.get('id', None)
        secret = request.GET.get('secret', None)

    payload = None
    if request.method == 'POST':
        payload = json.loads(request.body)
        id = payload.get('id')
        secret = payload.get('secret')

    if id is None \
            or secret is None \
            or not is_valid_secret(id, secret):
        return HttpResponse('You are not allowed to edit this item', status=401)

    item = es.get(index='object', doc_type='item', id=id)

    if item is None:
        return HttpResponse('There is no item by this id', status=401)

    if request.method == 'GET':
        return render(request, "map/item.html", {'item': json.dumps(item), 'secret': secret})

    if request.method == 'POST':
        return edit_item(payload)

    return HttpResponse(status=401)


def new_item(request):
    if request.method == 'GET':
        id = request.GET.get('id', None)
        if id is None:
            return render(request, "map/new_item.html", {})

        item = get_item_by_id(id)
        item_json = None
        if item is not None:
            item_json = json.dumps(item)

        return render(request, "map/new_item.html", {'item': item_json})
    if request.method == 'POST':
        return handle_new_item_post(json.loads(request.body))

    return HttpResponse(status=401)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def get_item_by_id(id):
    return
