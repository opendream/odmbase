# -*- coding: utf-8 -*-

# Application definition

APPEND_INSTALLED_APPS = (
)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'project_implement_override',
        'USER': 'project_implement_override',
        'PASSWORD': 'project_implement_override',
        'HOST': ''
    }
}

STATIC_URL = '/static/'
SITE_NAME = 'project_implement_override.com'
SITE_SLOGAN = 'project_implement_override'
DEFAULT_FROM_EMAIL = 'project_implement_override <no-reply@project_implement_override.com>'
SITE_DOMAIN = 'project_implement_override.com'
SITE_URL = 'http://%s' % SITE_DOMAIN
SITE_LOGO_URL = '%simages/logo-project_implement_override.png' % STATIC_URL
SITE_FAVICON_URL = '%simages/favicon-project_implement_override.png' % STATIC_URL

GOOGLE_ANALYTICS_KEY = ''
REGISTER_CONFIRM = False