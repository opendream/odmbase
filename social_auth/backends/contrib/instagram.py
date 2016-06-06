from urllib import urlencode

try:
    import json as simplejson
except ImportError:
    try:
        import simplejson
    except ImportError:
        from django.utils import simplejson

from social_auth.backends import BaseOAuth2, OAuthBackend
from social_auth.utils import dsa_urlopen


INSTAGRAM_SERVER = 'instagram.com'
INSTAGRAM_AUTHORIZATION_URL = 'https://api.instagram.com/oauth/authorize'
INSTAGRAM_ACCESS_TOKEN_URL = 'https://api.instagram.com/oauth/access_token'
INSTAGRAM_CHECK_AUTH = 'https://api.instagram.com/v1/users/self'


class InstagramBackend(OAuthBackend):
    name = 'instagram'

    @classmethod
    def extra_data(cls, user, uid, response, details=None):
        """Return access_token and extra defined names to store in
        extra_data field"""
        data = super(InstagramBackend, cls).extra_data(user, uid, response,
                                                       details)
        try:
            data['username'] = response['data']['username']
        except KeyError:
            pass
        return data

    def get_user_id(self, details, response):
        return response['data']['id']

    def get_user_details(self, response):

        """Return user details from Instagram account"""
        username = response['data']['username']
        fullname = response['data'].get('full_name', '')
        email = response['data'].get('email', '')

        first_name = fullname
        last_name = ''
        if len(fullname.split(' ')) == 2:
            first_name, last_name = fullname.split(' ')

        return {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }


class InstagramAuth(BaseOAuth2):
    """Instagram OAuth mechanism"""
    AUTHORIZATION_URL = INSTAGRAM_AUTHORIZATION_URL
    ACCESS_TOKEN_URL = INSTAGRAM_ACCESS_TOKEN_URL
    AUTH_BACKEND = InstagramBackend
    SETTINGS_KEY_NAME = 'INSTAGRAM_CLIENT_ID'
    SETTINGS_SECRET_NAME = 'INSTAGRAM_CLIENT_SECRET'

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        params = {'access_token': access_token}
        url = INSTAGRAM_CHECK_AUTH + '?' + urlencode(params)
        try:
            return simplejson.load(dsa_urlopen(url))
        except ValueError:
            return None


# Backend definition
BACKENDS = {
    'instagram': InstagramAuth,
}
