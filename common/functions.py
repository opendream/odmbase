
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.utils.translation import ugettext_lazy as _


from django import template
from django.utils.safestring import mark_safe
from django.utils.text import normalize_newlines, slugify

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import re
import uuid as _uu

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