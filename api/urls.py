from django.conf.urls import patterns, include
from tastypie.api import Api

v1_api = Api(api_name='v1')

# Common
from odmbase.common.api import CommonResource, ImageResource
v1_api.register(CommonResource())
v1_api.register(ImageResource())

# Account
from account.api import UserResource
v1_api.register(UserResource())
from api.registers import API_RESOURCES
try:


    from api.registers import API_RESOURCES
    print API_RESOURCES
    for resource in API_RESOURCES:
        print resource
        v1_api.register(resource)

except ImportError:
    pass

from odmbase.account.api import SocialSignResource

urlpatterns = patterns('',
    (r'v1/user/', include(SocialSignResource().urls)),
    (r'', include(v1_api.urls)),
)
