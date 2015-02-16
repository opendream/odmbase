from django.conf import settings

from odmbase.common.constants import STATUS_PENDING, STATUS_PUBLISHED, STATUS_DRAFT, STATUS_DELETED


def helper(request):

    context = {
        'BASE_URL': request.build_absolute_uri('/')[0:-1],
        'SITE_LOGO_URL': settings.SITE_LOGO_URL,
        'SITE_NAME': settings.SITE_NAME,
        'SITE_SLOGAN': settings.SITE_SLOGAN,
        'SITE_FAVICON_URL': settings.SITE_FAVICON_URL,
        'STATUS_PUBLISHED': STATUS_PUBLISHED,
        'STATUS_PENDING': STATUS_PENDING,
        'STATUS_DRAFT': STATUS_DRAFT,
        'STATUS_DELETED': STATUS_DELETED,
        'GOOGLE_ANALYTICS_KEY': settings.GOOGLE_ANALYTICS_KEY,
        'SITE_URL': settings.SITE_URL,

        'DEBUG': int(settings.DEBUG)
    }

    return context
