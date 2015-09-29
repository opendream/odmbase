from django.conf import settings

from odmbase.common.constants import STATUS_PENDING, STATUS_PUBLISHED, STATUS_DRAFT, STATUS_DELETED


def helper(request):

    context = {
        'BASE_URL': request.build_absolute_uri('/')[0:-1],
        'SITE_LOGO_URL': settings.SITE_LOGO_URL,
        'SITE_NAME': settings.SITE_NAME,
        'SITE_SLOGAN': settings.SITE_SLOGAN,
        'SITE_FAVICON_URL': settings.SITE_FAVICON_URL,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'STATUS_PUBLISHED': STATUS_PUBLISHED,
        'STATUS_PENDING': STATUS_PENDING,
        'STATUS_DRAFT': STATUS_DRAFT,
        'STATUS_DELETED': STATUS_DELETED,
        'GOOGLE_ANALYTICS_KEY': settings.GOOGLE_ANALYTICS_KEY,
        'SITE_URL': settings.SITE_URL,
        'NG_APP': settings.NG_APP,
        'DEBUG': int(settings.DEBUG),
        'ENABLE_COMMENT': settings.ENABLE_COMMENT,
        'ENABLE_LIKE': settings.ENABLE_LIKE,
        'ENABLE_MESSAGE': settings.ENABLE_MESSAGE,
    }

    try:
        context['SOCIAL_FEED_TAGS'] = settings.SOCIAL_FEED_TAGS
    except:
        pass

    return context
