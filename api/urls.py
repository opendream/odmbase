from django.conf.urls import patterns, include
from tastypie.api import Api

v1_api = Api(api_name='v1')

# Common
from odmbase.common.api import CommonResource, ImageResource
v1_api.register(CommonResource())
v1_api.register(ImageResource())

# Account
from odmbase.account.api import UserResource
v1_api.register(UserResource())


urlpatterns = patterns('',
    (r'', include(v1_api.urls)),
)