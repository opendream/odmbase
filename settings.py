# -*- coding: utf-8 -*-
"""
Django settings for odmbase project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f#ld80*+=)j_j_if^rw6jipxlhg%$=*z)2n_1!by9o7pl!yu%1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Lib
    'tastypie',
    'sorl.thumbnail',
    'social_auth',

    # Project
    'odmbase',
    'odmbase.common',
    'account',

    #'odmbase.account',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',

    'odmbase.common.context_processors.helper'
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'conf/templates'),
    os.path.join(BASE_DIR, 'odmbase/templates'),
    os.path.join(BASE_DIR, 'static/app'),
    os.path.join(BASE_DIR, 'templates'),
)

ROOT_URLCONF = 'odmbase.urls'

WSGI_APPLICATION = 'odmbase.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'project_implement',
        'USER': 'project_implement',
        'PASSWORD': 'project_implement',
        'HOST': ''
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'sitestatic/')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Account
AUTH_USER_MODEL = 'account.User'
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    # TODO: Implement later
    #'social_auth.backends.twitter.TwitterBackend',
    #'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'odmbase.account.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend'
)

LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/account/error/'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# DJANGO SOCIAL AUTH

SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_SESSION_EXPIRATION = False
SOCIAL_AUTH_UUID_LENGTH = 22

FACEBOOK_APP_ID = '445472018940505'
FACEBOOK_API_SECRET = '55bdd2f3c977a370255a5713af4121e2'
FACEBOOK_EXTENDED_PERMISSIONS = ['email']


#LOGIN_URL = '/account/login/'
#LOGIN_REDIRECT_URL = '/'
#LOGIN_ERROR_URL = '/account/error/'

SOCIAL_AUTH_USER_MODEL = 'account.User'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
SOCIAL_AUTH_BACKEND_ERROR_URL = '/account/error/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/account/redirect/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/account/redirect/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/account/redirect/'
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'odmbase.account.pipeline.generate_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'odmbase.account.pipeline.update_user_details',
    'odmbase.account.pipeline.update_profile',
)

RESERVED_USERNAMES = [
    'admin',
]


# API
TASTYPIE_DEFAULT_FORMATS = ['json']


# CUSTOM PROJECT #############################

SITE_NAME = 'project_implement.com'
SITE_SLOGAN = 'Project Slogan'
DEFAULT_FROM_EMAIL = 'Panjai <no-reply@project_implement.com>'
SITE_DOMAIN = 'project_implement.com'
SITE_URL = 'http://%s' % SITE_DOMAIN
SITE_LOGO_URL = '%simages/logo-project_implement.png' % STATIC_URL
SITE_FAVICON_URL = '%simages/favicon-project_implement.png' % STATIC_URL

GOOGLE_ANALYTICS_KEY = ''
REGISTER_CONFIRM = False


# Overide settings
try:
    from conf.settings import *

    INSTALLED_APPS += APPEND_INSTALLED_APPS

except ImportError:
    print 'Please, implement project see README.md'


try:
    from conf.settings_local import *
except ImportError:
    pass

# TESTING #####################################################################
if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
    MEDIA_URL = '/test_media/'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if 'runserver' in sys.argv:
    DEBUG = True

# DEBUG MODE ##################################################################

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    GOOGLE_ANALYTICS_KEY = ''

    SITE_DOMAIN = 'localhost:8000'
    SITE_URL = 'http://%s' % SITE_DOMAIN
