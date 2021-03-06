from django.conf import settings
from django.conf.urls import patterns, include, url
from tastypie.api import Api

v1_api = Api(api_name='v1')

# Common
from odmbase.common.api import CommonResource, ImageResource, PageNotFoundResource
v1_api.register(CommonResource())
v1_api.register(ImageResource())
v1_api.register(PageNotFoundResource())

# Account
from account.api import UserResource
v1_api.register(UserResource())

# Search
from odmbase.search.api import SearchResource
v1_api.register(SearchResource())


try:

    from api.registers import API_RESOURCES

    for resource in API_RESOURCES:
        v1_api.register(resource)


except ImportError:
    pass


if settings.ENABLE_COMMENT:
    from odmbase.comments.api import CommentResource
    v1_api.register(CommentResource())

if settings.ENABLE_LIKE:
    from odmbase.likes.api import LikeResource
    v1_api.register(LikeResource())

if settings.ENABLE_MESSAGE:
    from odmbase.message.api import MessageResource
    v1_api.register(MessageResource())

from odmbase.account.api import SocialSignResource

urlpatterns = patterns('',
    url(r'v1/website-meta/$', 'odmbase.common.api.scrap_website_meta', name='scrap_website_meta'),
    (r'v1/user/', include(SocialSignResource().urls)),
    (r'', include(v1_api.urls)),
)
