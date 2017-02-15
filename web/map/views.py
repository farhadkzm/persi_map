import json
import requests
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader
from elasticsearch import Elasticsearch
import re

es = Elasticsearch([{
    'host': 'search-persi-es-4zjjaw2exoo73nq2xbq3mvulie.us-west-2.es.amazonaws.com', 'port': 443, 'use_ssl': True
}])


def create_new_item(request):
    return JsonResponse('')


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


def new_item(request):
    if request.method == 'GET':
        return render(request, "map/new_item.html", {})

    if request.method == 'POST':
        return handle_new_item_post(request)

    return index(request)


def check_recaptcha(payload):
    recaptcha_request_payload = {'secret': '6LfiNhUUAAAAAO7owWIr66Fo8l_pMFASfhYvxZxF',
                                 'response': payload.get('recaptcha')}
    r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                      data=recaptcha_request_payload)
    return r.json().get('success')


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def handle_new_item_post(request):
    payload = json.loads(request.body)

    recaptcha_success = check_recaptcha(payload)

    if not recaptcha_success:
        return HttpResponse(status=401)

    data = {
        'type': category,
        'src': 'peri_map',
        'name': name,
        'detail': {

            'occupation': occ,
            'gender': gender,
        },

        'location': {
            'phone': '',
            'address': address_line.strip(),
            'geo_set': {
                "lat": latitude,
                "lon": longitude
            }
        },
    }
    # store data in elasticsearch
    res = es.index(index='object', doc_type='item', id=1, body=data)
    # send email
    print payload
    return HttpResponse()
