import os
import random
import re
import urllib
import urllib2
import uuid as _uu

from django import template
from django.conf import settings
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.core.files import File
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.utils.text import normalize_newlines, slugify
from django.utils.translation import ugettext_lazy as _

from bs4 import BeautifulSoup

register = template.Library()

def camelcase_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def underscore_to_camelcase(name):
    return ''.join([c.title() for c in name.split('_')])

def remove_newlines(text):
    """
    Removes all newline characters from a block of text.
    """
    # First normalize the newlines using Django's nifty utility
    normalized_text = normalize_newlines(text)
    # Then simply remove the newlines like so.
    return mark_safe(normalized_text.replace('\n', ' '))


def staff_required(request):
    defaults = {
        'template_name': 'admin/login.html',
        'authentication_form': AdminAuthenticationForm,
        'extra_context': {
            'title': _('Log in'),
            'app_path': request.get_full_path(),
            REDIRECT_FIELD_NAME: request.get_full_path(),
        },
    }
    return login(request, **defaults)

def instance_set_permalink(instance, title, field_name='permalink'):
    ModelClass = instance.__class__

    permalink = slugify(title)

    increment_number = 1

    while True:
        try:
            ModelClass.objects.get(**{field_name: permalink})
        except ModelClass.DoesNotExist:
            setattr(instance, field_name, permalink)
            break

        permalink = "%s-%s" % (permalink, increment_number)
        increment_number = increment_number + 1

def reference_exist(instance, field_name):
    if instance.id and hasattr(instance, field_name):
        field_value = getattr(instance, field_name)
    else:
        return False

    if hasattr(field_value, 'id') and getattr(field_value, 'id'):
        return field_value
    return False


def uuid(url=None):

    _ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    # If no URL is given, generate a random UUID.
    if url is None:
        unique_id = _uu.uuid4().int
    else:
        unique_id = _uu.uuid3(_uu.NAMESPACE_URL, url).int

    alphabet_length = len(_ALPHABET)
    output = []
    while unique_id > 0:
        digit = unique_id % alphabet_length
        output.append(_ALPHABET[digit])
        unique_id = int(unique_id / alphabet_length)
    return "".join(output)

def generate_key(number, prefix=''):
    prefix = prefix and ('%s-' % prefix)
    return '%s%s-%s' % (prefix, urlsafe_base64_encode(force_bytes(number)), uuid(number))


def instance_save_image_from_url(instance, image_url, field_name='image', rand=False):
    # Use save_form_data like model form
    image_field = instance._meta.get_field(field_name)
    if image_field:
        # determined temp path of file widget
        file_name = image_url.split('?')[0]
        file_name_list = file_name.split('/')

        # find the name of file
        while len(file_name_list):
            file_name = file_name_list.pop()
            if file_name:
                if not re.search('_(\d+)\.(jpg|jpef|png|gif)$', file_name, re.IGNORECASE):
                    file_name = '%s.jpg' % file_name
                break


        if rand:
            image_url = '%s?a=%s' % (image_url, random.randint(1, 100000000000))

        result = urllib.urlretrieve(image_url)

        image_file = getattr(instance, field_name)
        image_file.save(file_name, File(open(result[0])))
        #instance.save()

    else:
        raise AttributeError


def scrap_website_meta(url):
    try:
        raw = urllib2.urlopen(url, timeout=10)
    except:
        return {}

    charset = raw.headers.getparam('charset') or 'utf-8'
    html = raw.read()
    try:
        html = html.decode(charset)
    except:
        pass
    doc = BeautifulSoup(html)

    return {
        'url': url,
        'title': _scrap_title(doc),
        'description': _scrap_description(doc),
        'image': _scrap_image(doc, raw.geturl()),
    }

def _scrap_title(doc):
    if doc.find(property='og:title'):
        title = doc.find(property='og:title')['content']
    elif doc.find(attrs={'name': 'twitter:title'}):
        title = doc.find(attrs={'name': 'twitter:title'})['content']
    else:
        title = doc.head.title.text
    return title

def _scrap_description(doc):
    description = ''
    if doc.find(property='og:description'):
        description = doc.find(property='og:description')['content']
    elif doc.find(attrs={'name': 'twitter:description'}):
        description = doc.find(attrs={'name': 'twitter:description'})['content']
    elif doc.find(attrs={'name': 'description'}):
        description = doc.find(attrs={'name': 'description'})['content']
    elif doc.h1:
        description = strip_tags(doc.h1).strip()
    elif doc.p:
        description = strip_tags(doc.p).strip()

    if len(description) > 200:
        return description[:200] + '...'
    return description or ''

def _scrap_image(doc, url):
    image = ''
    if doc.find(property='og:image'):
        image = doc.find(property='og:image')['content']
    elif doc.find(attrs={'name': 'twitter:image:src'}):
        image = doc.find(attrs={'name': 'twitter:image:src'})['content']
    elif doc.find(itemprop='image'):
        image = doc.find(itemprop='image')['content']
    else:
        images = doc.html.body.findAll('img')
        if images:
            attrs = dict(images[0].attrs)
            if 'ng-src' in attrs:
                image = attrs['ng-src']
            else:
                image = attrs['src']

    if image and ( not image.startswith('http') and not image.startswith('ftp') ):
        url_splitted = url.split('/', 3)
        url_origin = '/'.join(x for x in url_splitted[:-1] )
        if image.startswith('/'):
            image = url_origin + image
        else:
            image = url_origin + '/' + image

    return image


def _send_mail(subject, email, from_email, send_email,
    html_message, fail_silently=True, immediately=False):

    site_url = settings.SITE_URL
    c = {
        'content': email,
        'site_url': site_url,
    }

    email = loader.render_to_string('email/template.html', c)

    if immediately:
        from django.core.mail import send_mail
        try:
            send_mail(subject, email, from_email, send_email,
                  html_message=email, fail_silently=fail_silently)
        except:
            pass

    else:
        try:
            from utilities.tasks import _send_mail as send_mail
            send_mail.delay(subject, email, from_email, send_email,
                html_message=email, fail_silently=fail_silently)
        except:
            from django.core.mail import send_mail
            send_mail(subject, email, from_email, send_email,
                html_message=email, fail_silently=fail_silently)
