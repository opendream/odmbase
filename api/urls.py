from django.conf.urls import patterns, include
from tastypie.api import Api

v1_api = Api(api_name='v1')

# Common
from odmbase.common.api import CommonResource, ImageResource
v1_api.register(CommonResource())
v1_api.register(ImageResource())

# Account
from odmbase.account.api import UserResource, SocialSignResource
v1_api.register(UserResource())

try:

    from api.registers import API_RESOURCES
    for resource in API_RESOURCES:
        v1_api.register(resource)

except ImportError:
    pass

urlpatterns = patterns('',
    (r'v1/user/', include(SocialSignResource().urls)),
    (r'', include(v1_api.urls)),
)