from collections import namedtuple
import mimetypes
import re
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, render_to_response
from django.db import models
from django.template.defaultfilters import truncatechars
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import urllib2
import urllib
from bs4 import BeautifulSoup

# =============================
# Home
# =============================
import requests
from odmbase.common.models import CommonModel, PageNotFound


def home(request):

    meta = ''
    model = None
    status_code = 200

    try:
        model = {'seo_meta': settings.SITE_META_PAGES[request.path[1:]]}
    except:
        pass

    if not model:
        for Model in models.get_models():


            if hasattr(Model, 'URL_PATTERN'):

                regex = re.compile(Model.URL_PATTERN)
                match = regex.search(request.path[1:])

                if match:
                    # TODO: Check reserve urls
                    try:
                        model = Model.objects.get(**match.groupdict())
                    except Model.DoesNotExist:
                        pass

                    break

    if not model:

        if request.path != '/':
            try:
                PageNotFound.objects.get(path=request.path)
                status_code = 404
            except PageNotFound.DoesNotExist:
                pass

        model = {'seo_meta': {
            'title': settings.SITE_SLOGAN,
            'description': settings.SITE_DESCRIPTION,
            'image': settings.SITE_LOGO_URL
        }}

    meta = render_to_string('meta.html', {
        'site_name': settings.SITE_NAME,
        'base_url': request.build_absolute_uri('/')[0:-1],
        'current_url': request.build_absolute_uri(),
        'model': model,
    })

    # TODO: add default meta to list page and gome page

    page_title = settings.SITE_NAME
    if model:
        try:
            title = model.seo_meta().get('title')
            page_title = '%s | %s' % (truncatechars(title, 50), settings.SITE_NAME)
        except (AttributeError, TypeError):
            pass

    if request.GET.get('get_title'):
        return HttpResponse(page_title)
    else:
        return render(request, 'base.html', {'meta': meta, 'page_title': page_title}, status=status_code)


def handler403(request):
    return render(request, '403.html')

def social_count_gplus(request):
    url = request.GET['url']
    r = requests.get('https://plusone.google.com/_/+1/fastbutton', params={'url': url}, headers={'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'})
    html = r.text
    doc = BeautifulSoup(html)
    count = doc.find(id='aggregateCount')
    return HttpResponse(count)


def crawl_index(request):
    content_list = CommonModel.objects.filter(status__gt=0).order_by('-changed', '-created')
    paginator = Paginator(content_list, 25)  # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        contents = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contents = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contents = paginator.page(paginator.num_pages)

    return render_to_response('list.html', {"contents": contents})


def proxy(request):

    url = request.GET.get('url')

    try:
        contents = urllib2.urlopen(url).read()
    except urllib2.HTTPError:
        # Naive to assume a 404 - ed
        raise Http404, '"%s" does not exist' % url  # RAISE
    else:
        # Found the doc. Return it to response.
        mimetype = mimetypes.guess_type(url)
        response = HttpResponse(contents, content_type=mimetype)

        # Success! We have the file. Send it back.
        return response
>>>>>>> c1f1eb925622deeec17556b6ba18656561593d57
