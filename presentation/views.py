import re
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.db import models
from django.template.loader import render_to_string

import urllib2
import urllib
from bs4 import BeautifulSoup

# =============================
# Home
# =============================
import requests


def home(request):

    meta = ''

    for Model in models.get_models():

        if hasattr(Model, 'URL_PATTERN'):

            regex = re.compile(Model.URL_PATTERN)
            match = regex.search(request.path[1:])

            if match:
                # TODO: Check reserve urls
                try:
                    model = Model.objects.get(**match.groupdict())
                except Model.DoesNotExist:
                    model = None

                meta = render_to_string('meta.html', {
                    'site_name': settings.SITE_NAME,
                    'base_url': request.build_absolute_uri('/')[0:-1],
                    'current_url': request.build_absolute_uri(),
                    'model': model,
                })

                break

    # TODO: add default meta to list page and gome page

    return render(request, 'base.html', {'meta': meta})


def handler403(request):
    return render(request, '403.html')

def social_count_gplus(request):
    url = request.GET['url']
    r = requests.get('https://plusone.google.com/_/+1/fastbutton', params={'url': url}, headers={'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'})
    html = r.text
    doc = BeautifulSoup(html)
    count = doc.find(id='aggregateCount')
    return HttpResponse(count)