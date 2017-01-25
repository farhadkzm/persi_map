from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from elasticsearch import Elasticsearch

es = Elasticsearch(['search:9200'], max_retries=10)


# search queries to be implemented:
#
def search(request):

    geo_piont = {
        "lat": float(request.GET.get('lat', 0)),
        "lon": float(request.GET.get('lng', 0))
    }
    distance = request.GET.get('distance', '')
    category = request.GET.get('category', '')
    name = request.GET.get('name', '')
    occupation = request.GET.get('occupation', '')
    clinic = request.GET.get('clinic', '')
    matching_blocks = []
    if name != '':
        matching_blocks.append({"match": {"name": name}})

    if occupation != '':
        matching_blocks.append( {"match": {"detail.occupation": occupation}})

    if clinic != '':
        matching_blocks.append({"match": {"location.clinic_name": clinic}})

    print 'printing matching blocks'
    print matching_blocks
    search_body = {
        "query": {
            "bool": {
                "must": matching_blocks,
                "filter": [
                    {
                        "geo_distance": {
                            "distance": distance,
                            "location.geo_set": geo_piont
                        }
                    },
                    {"term": {"type": category}}
                ]
            }
        }
    }

    result = es.search(index='object', doc_type='item', body=search_body, filter_path=['hits.hits._*'])
    return JsonResponse(result)


def index(request):
    template = loader.get_template('map/index.html')

    return HttpResponse(template.render({}, request))
