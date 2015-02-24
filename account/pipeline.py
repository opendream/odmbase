
from django.contrib.auth import get_user_model

from social_auth.backends.pipeline.user import _ignore_field
from social_auth.db.django_models import UserSocialAuth


from django.conf import settings
from odmbase.common.functions import instance_save_image_from_url

User = get_user_model()

def rewrite_username(username):

    _username_ = username.lower().split('@')[0].replace(' ', '.')
    username = _username_
    usernames = [u for u in User.objects.values_list('username', flat=True)]
    usernames = usernames + settings.RESERVED_USERNAMES
    increment_number = 1
    while True:
        if username in usernames:
            username = "%s%s" % (_username_, increment_number)
            increment_number += 1
        else:
            break

    return username

def generate_username(details, user=None, user_exists=UserSocialAuth.simple_user_exists, *args, **kwargs):
    if user:
        return {'username': user.username}
    username = rewrite_username(details['username'])

    return {'username': username}


def update_profile(backend, details, response, user=None, is_new=False, *args, **kwargs):
    if not details['email']:
        # TODO: update email
        pass

    print details

    user.first_name = user.first_name or details.get('first_name')
    user.last_name = user.last_name or details.get('last_name')

    print user.first_name

    if hasattr(user, 'gender') and not user.gender and response.get('gender'):
        user.gender = response.get('gender')

    if not user.image:
        fb_image_url = "https://graph.facebook.com/%s/picture?type=large" % response['id']
        instance_save_image_from_url(user, fb_image_url)


def update_user_details(backend, details, response, user=None, is_new=False,
                                *args, **kwargs):


    if user is None:
        return

    is_deleted = user.is_deleted

    if is_deleted:
        user.is_deleted = False
    else:
        return

    changed = False  # flag to track changes

    for name, value in details.iteritems():
        # do not update username, it was already generated, do not update
        # configured fields if user already existed
        if not _ignore_field(name, is_new):
            if value and value != getattr(user, name, None):
                setattr(user, name, value)
                changed = True

    if changed or is_deleted:
        user.save()