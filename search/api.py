# -*- encoding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.db.models.loading import get_model
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from tastypie import fields
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.resources import Resource
from odmbase.common.api import CommonApiKeyAuthentication

User = get_user_model()

try:
    from conf.search import RESOURCE_MAP
except ImportError:
    try:
        from account.api import UserReferenceResource
        RESOURCE_MAP = {User: UserReferenceResource}
    except ImportError:
        from odmbase.account.api import UserReferenceResource
        RESOURCE_MAP = {User: UserReferenceResource}


class SearchObject(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class SearchResource(Resource):
    item = GenericForeignKeyField(RESOURCE_MAP, 'object', readonly=True, full=True, null=True)
    score = fields.FloatField(attribute='score', readonly=True, blank=True, null=True)

    class Meta:
        resource_name = 'search'
        object_class = SearchObject
        authentication = CommonApiKeyAuthentication()


    def get_object_list(self, request):


        params = request.GET

        sqs = SearchQuerySet()

        if len(params.getlist('content_type')):
            for content_type in params.getlist('content_type'):
                sqs = sqs.models(get_model(*content_type.split('.')))

        #if params.get('order_by'):
        #    sqs = sqs.order_by(params.get('order_by', ''))

        if params.get('q', ''):
            sqs = sqs.filter_or(content=AutoQuery(params.get('q', '').lower()))

        for k, v in params.iteritems():
            if k not in ['q', 'page', 'limit', 'content_type', 'order_by']:
                sqs = sqs.filter_or(**{k: v})

        limit = int(request.GET.get('limit', 20))

        page = int(request.GET.get('page', 1)) - 1
        object_list = sqs[page * limit:(page * limit + limit)]

        objects = []

        for result in object_list:
            objects.append(result)

        return objects

    def obj_get_list(self, bundle, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(bundle.request)