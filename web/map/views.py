from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
import urllib
import json
from django.http import JsonResponse
import requests

def search(request):
    # todo convert address to geo point
    # todo search ES with e geo point
    # todo return the result
    lat = float(request.GET.get('lat', 0))
    lng = float(request.GET.get('lng', 0))
    distance = request.GET.get('distance', '')
    payload = {
        "query": {
            "bool": {
                "must": {
                    "match_all": {}
                },
                "filter": {
                    "geo_distance": {
                        "distance": distance,
                        "address.location": {
                            "lat": lat,
                            "lon": lng
                        }
                    }
                }
            }
        }
    }

    link = "http://search:9200/objects/items/_search"

    myfile = requests.post(link, json=payload)
    print(myfile.text)
    return JsonResponse(myfile.json())

def index(request):
    template = loader.get_template('map/index.html')

    return HttpResponse(template.render({}, request))
