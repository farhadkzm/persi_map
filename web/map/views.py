import hashlib
import json
import re
import requests
import smtplib
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader
from elasticsearch import Elasticsearch



salt = '7b4dafa43458d3a6a232afdd184ecb53'


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
        id = request.GET.get('id', None)
        if id is None:
            return render(request, "map/new_item.html", {})

        item = get_item_by_id(id)
        item_json = None
        if item is not None:
            item_json = json.dumps(item)

        return render(request, "map/new_item.html", {'item': item_json})
    if request.method == 'POST':
        return handle_new_item_post(request)

    return HttpResponse(status=401)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def send_email(payload):
    sender = 'from@fromdomain.com'
    receivers = [payload.get('email')]
    smtp_server = 'localhost'
    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    This is a test e-mail message.
    """

    try:
        smtpObj = smtplib.SMTP(smtp_server)
        smtpObj.sendmail(sender, receivers, message)
        print "Successfully sent email"
        return False
    except SMTPException:
        print "Error: unable to send email"
        return True


def get_item_by_id(id):
    return es.get(index='object', doc_type='item', id=id)


def item_exists(id):
    return es.exists(index='object', doc_type='item', id=id)

