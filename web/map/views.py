import requests
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from elasticsearch import Elasticsearch

es = Elasticsearch(['search:9200'], max_retries=10)
def search(request):


    geo_piont = {
        "lat": float(request.GET.get('lat', 0)),
        "lon": float(request.GET.get('lng', 0))
    }
    distance = request.GET.get('distance', '')
    search_body = {
        "query": {
            "bool": {
                "must": {
                    "match_all": {}
                },
                "filter": {
                    "geo_distance": {
                        "distance": distance,
                        "location.geo_set": geo_piont
                    }
                }
            }
        }
    }

    result = es.search(index='object', doc_type='item', body=search_body, filter_path=['hits.hits._*'])
    return JsonResponse(result)


def index(request):
    template = loader.get_template('map/index.html')

    return HttpResponse(template.render({}, request))
