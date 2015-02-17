from django.conf.urls import patterns, include
from tastypie.api import Api

v1_api = Api(api_name='v1')

# Common
from odmbase.common.api import CommonResource, ImageResource
v1_api.register(CommonResource())
v1_api.register(ImageResource())

# Account
from odmbase.account.api import UserResource, SocialSignUpResource
v1_api.register(UserResource())
v1_api.register(SocialSignUpResource())

try:

    from api.registers import API_RESOURCES
    for resource in API_RESOURCES:
        v1_api.register(resource)

except ImportError:
    pass

urlpatterns = patterns('',
    (r'', include(v1_api.urls)),
)