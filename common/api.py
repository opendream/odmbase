import json
import ast

from django.conf import settings
from django.conf.urls import url
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import six
from django.utils.cache import patch_vary_headers, patch_cache_control
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest, Unauthorized, ApiFieldError
from tastypie.fields import ToManyField, NOT_PROVIDED
from tastypie.http import HttpForbidden
from tastypie.resources import ModelResource, csrf_exempt, sanitize, BaseModelResource, DeclarativeMetaclass, \
    ModelDeclarativeMetaclass
from tastypie.serializers import Serializer
from tastypie import http
from tastypie import fields
from django.core.serializers import json as djangojson
from tastypie.utils import trailing_slash
from odmbase.api.fields import SorlThumbnailField
from odmbase.common.constants import STATUS_PUBLISHED

from odmbase.common.models import CommonModel, Image


class VerboseSerializer(Serializer):
    def to_json(self, data, options=None):
        """
        Given some Python data, produces JSON output.
        """
        if hasattr(data, 'get') and data.get('error'):
            try:
                data['error'] = ast.literal_eval(data['error'])
            except SyntaxError:
                pass

        options = options or {}
        data = self.to_simple(data, options)

        return djangojson.json.dumps(data, cls=djangojson.DjangoJSONEncoder, sort_keys=True, ensure_ascii=False)


    # Tastypie>=0.9.6,<=0.11.0
    def from_json(self, content):

        try:
            return json.loads(content)
        except ValueError as e:
            raise BadRequest(u"Incorrect JSON format: Reason: \"{}\" (See www.json.org for more info.)".format(e.message))


class CommonApiKeyAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):

        key_auth_check = super(CommonApiKeyAuthentication, self).is_authenticated(request, **kwargs)
        if request.method == 'GET' or key_auth_check:
            return True

        return key_auth_check



class CommonAnonymousPostApiKeyAuthentication(CommonApiKeyAuthentication):

    def is_authenticated(self, request, **kwargs):

        if request.method in ['GET', 'POST'] and not request.META.get('HTTP_AUTHORIZATION'):
            return True
        else:
            return super(CommonAnonymousPostApiKeyAuthentication, self).is_authenticated(request, **kwargs)

    def get_identifier(self, request):

        if request.method in ['GET', 'POST']:
            return "%s_%s" % (request.META.get('REMOTE_ADDR', 'noaddr'), request.META.get('REMOTE_HOST', 'nohost'))
        else:
            return super(CommonAnonymousPostApiKeyAuthentication, self).get_identifier(request)


    def extract_credentials(self, request):

        if request.META.get('HTTP_AUTHORIZATION') and request.META['HTTP_AUTHORIZATION'].lower().startswith('apikey '):
            (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

            if auth_type.lower() != 'apikey':
                raise ValueError("Incorrect authorization header.")

            username, api_key = data.split(':', 1)
        else:
            username = request.GET.get('username') or request.POST.get('username')
            api_key = request.GET.get('api_key') or request.POST.get('api_key')

        return username, api_key


class CommonAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # TODO : can see draft pendding status
        return object_list

    def read_detail(self, object_list, bundle):

        if hasattr(bundle.obj, 'status') and bundle.obj.status in [STATUS_PUBLISHED]:
            return True

        if bundle.obj.user_can_edit(bundle.request.user):
            return True

        if not hasattr(bundle.obj, 'status'):
            return True

        return False

    def create_list(self, object_list, bundle):

        if bundle.request.user.is_authenticated():
            return object_list
        return []

    def create_detail(self, object_list, bundle):
        return bundle.request.user.is_authenticated()


    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user_can_edit(bundle.request.user):
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.user_can_edit(bundle.request.user)

    def delete_list(self, object_list, bundle):
        return self.update_list(object_list, bundle)

    def delete_detail(self, object_list, bundle):
        return self.update_detail(object_list, bundle)


class CommonAnonymousPostAuthorization(CommonAuthorization):
    def create_detail(self, object_list, bundle):
        return True


class CommonModelDeclarativeMetaclass(ModelDeclarativeMetaclass):

    def __new__(cls, name, bases, attrs):
        meta = attrs.get('Meta')

        if meta and hasattr(meta, 'queryset'):
            setattr(meta, 'object_class', meta.queryset.model)

        new_class = super(CommonModelDeclarativeMetaclass, cls).__new__(cls, name, bases, attrs)

        setattr(new_class._meta, 'always_return_data', True)
        setattr(new_class._meta, 'serializer', VerboseSerializer(formats=['json']))

        #if not getattr(new_class._meta, 'authentication'):
        #setattr(new_class._meta, 'authentication', CommonApiKeyAuthentication())

        if getattr(new_class._meta, 'authorization').__class__ is ReadOnlyAuthorization:
            setattr(new_class._meta, 'authorization', CommonAuthorization())
            
        return new_class



class CommonModelResource(six.with_metaclass(CommonModelDeclarativeMetaclass, BaseModelResource)):

    unicode_string = fields.CharField(attribute='unicode_string', readonly=True)

    def build_schema(self):
        base_schema = super(CommonModelResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
            if f.name in base_schema['fields'] and f.choices:
                base_schema['fields'][f.name].update({
                    'choices': f.choices,
                })
        return base_schema

    def dehydrate(self, bundle):

        bundle = super(CommonModelResource, self).dehydrate(bundle)

        # Handle permission field abit
        bundle.data['can_edit'] = False
        if bundle.request.user and bundle.request.user.is_authenticated() and bundle.request.user.is_staff:
            bundle.data['can_edit'] = True
            return bundle

        if hasattr(bundle.obj, 'user_can_edit'):
            bundle.data['can_edit'] = bundle.obj.user_can_edit(bundle.request.user)
        else:
            if hasattr(self, 'CREATED_BY_FIELD'):
                bundle.data['can_edit'] = (getattr(bundle.obj, self.CREATED_BY_FIELD) == bundle.request.user)
            elif hasattr(bundle.obj, 'created_by'):
                bundle.data['can_edit'] = (bundle.obj.created_by == bundle.request.user)

        return bundle


    def put_detail(self, request, **kwargs):
        if not request.META.get('CONTENT_TYPE', 'application/json').startswith('application/json') and not hasattr(request, '_body'):
            request._body = ''

        return super(CommonModelResource, self).put_detail(request, **kwargs)

    def deserialize(self, request, data, format=None):

        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        if format == 'application/x-www-form-urlencoded':
            return request.POST

        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)

            return data

        return super(CommonModelResource, self).deserialize(request, data, format)

    def get_resource_uri(self, bundle_or_obj=None, url_name='api_dispatch_list'):

        resource_uri = super(CommonModelResource, self).get_resource_uri(bundle_or_obj, url_name)

        if hasattr(self._meta, 'return_resource') and self._meta.return_resource:
            resource_uri = resource_uri.replace(self._meta.resource_name, self._meta.return_resource._meta.resource_name)

        return resource_uri

    def wrap_view(self, view):
        """
        Wraps methods so they can be called in a more functional way as well
        as handling exceptions better.

        Note that if ``BadRequest`` or an exception with a ``response`` attr
        are seen, there is special handling to either present a message back
        to the user or return the response traveling with the exception.
        """

        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            try:
                callback = getattr(self, view)
                response = callback(request, *args, **kwargs)

                # Our response can vary based on a number of factors, use
                # the cache class to determine what we should ``Vary`` on so
                # caches won't return the wrong (cached) version.
                varies = getattr(self._meta.cache, "varies", [])

                if varies:
                    patch_vary_headers(response, varies)

                if self._meta.cache.cacheable(request, response):
                    if self._meta.cache.cache_control():
                        # If the request is cacheable and we have a
                        # ``Cache-Control`` available then patch the header.
                        patch_cache_control(response, **self._meta.cache.cache_control())

                if request.is_ajax() and not response.has_header("Cache-Control"):
                    # IE excessively caches XMLHttpRequests, so we're disabling
                    # the browser cache here.
                    # See http://www.enhanceie.com/ie/bugs.asp for details.
                    patch_cache_control(response, no_cache=True)

                return response
            except (BadRequest, fields.ApiFieldError) as e:
                data = {"error": sanitize(e.args[0]) if getattr(e, 'args') else ''}
                return self.error_response(request, data, response_class=http.HttpBadRequest)
            except ValidationError as e:
                data = {"error": sanitize(e)}

                return self.error_response(request, data, response_class=http.HttpBadRequest)
            except Exception as e:
                if hasattr(e, 'response'):
                    return e.response

                # A real, non-expected exception.
                # Handle the case where the full traceback is more helpful
                # than the serialized error.
                if settings.DEBUG and getattr(settings, 'TASTYPIE_FULL_DEBUG', False):
                    raise

                # Re-raise the error to get a proper traceback when the error
                # happend during a test case
                if request.META.get('SERVER_NAME') == 'testserver':
                    raise

                # Rather than re-raising, we're going to things similar to
                # what Django does. The difference is returning a serialized
                # error message.
                return self._handle_500(request, e)

        return wrapper

class CommonResource(CommonModelResource):

    class Meta:
        queryset = CommonModel.objects.all()
        resource_name = 'common'
        authentication = CommonApiKeyAuthentication()


class ImageAttachResource(CommonModelResource):

    image = fields.FileField(attribute='image', null=True)
    image_thumbnail_1x = SorlThumbnailField(attribute='image', thumb_options={'geometry': '400x400'}, readonly=True)
    image_thumbnail_2x = SorlThumbnailField(attribute='image', thumb_options={'geometry': '800x800'}, readonly=True)
    image_thumbnail_3x = SorlThumbnailField(attribute='image', thumb_options={'geometry': '1024x1024'}, readonly=True)

    def prepend_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/set_image%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('set_image'), name="api_set_image"),
        ]


    def set_image(self, request=None, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        #self.throttle_check(request)

        if not request.user:
            return self.create_response(
                request, {
                    'error': 'You are anonymous user',
                },
                HttpForbidden,
            )

        request.FILES # Holy
        return super(ImageAttachResource, self).put_detail(request, **kwargs)

'''
# Please, rewrite to single line
curl  -F "attach_to=api/v1/common/96/"
      -F "image=@static/images/default.png"
      -F "title=This is an image file"
      -F "description=You are developer"
localhost:8000/api/v1/image/
'''
class ImageResource(CommonModelResource):

    attach_to = fields.ForeignKey(CommonResource, 'attach_to', null=True)
    image = fields.FileField(attribute='image')
    image_thumbnail_1x = SorlThumbnailField(attribute='image', thumb_options={'geometry': '400x400'})
    image_thumbnail_2x = SorlThumbnailField(attribute='image', thumb_options={'geometry': '800x800'})
    image_thumbnail_3x = SorlThumbnailField(attribute='image', thumb_options={'geometry': '1024x1024'})

    unicode_string = fields.CharField(attribute='unicode_string', null=True)

    class Meta:
        queryset = Image.objects.all()
        resource_name = 'image'
        authentication = CommonApiKeyAuthentication()



class BetterManyToManyField(ToManyField):

    def __init__(self, to, attribute, related_name=None, default=NOT_PROVIDED,
                 null=False, blank=False, readonly=False, full=False,
                 unique=False, help_text=None, use_in='all', full_list=True, full_detail=True,
                 limit=None, filter=None):


        super(BetterManyToManyField, self).__init__(
            to, attribute, related_name=related_name, default=default,
            null=null, blank=blank, readonly=readonly, full=full,
            unique=unique, help_text=help_text, use_in=use_in,
            full_list=full_list, full_detail=full_detail
        )
        self.m2m_bundles = []
        self.limit = limit
        self.filter = filter


    def dehydrate(self, bundle, for_list=True):
        if not bundle.obj or not bundle.obj.pk:
            if not self.null:
                raise ApiFieldError(
                    "The model '%r' does not have a primary key and can not be used in a ToMany context." % bundle.obj)

            return []

        the_m2ms = None
        previous_obj = bundle.obj
        attr = self.attribute

        if isinstance(self.attribute, six.string_types):
            attrs = self.attribute.split('__')
            the_m2ms = bundle.obj

            for attr in attrs:
                previous_obj = the_m2ms
                try:
                    the_m2ms = getattr(the_m2ms, attr, None)
                except ObjectDoesNotExist:
                    the_m2ms = None

                if not the_m2ms:
                    break

        elif callable(self.attribute):
            the_m2ms = self.attribute(bundle)

        if not the_m2ms:
            if not self.null:
                raise ApiFieldError(
                    "The model '%r' has an empty attribute '%s' and doesn't allow a null value." % (previous_obj, attr))

            return []

        self.m2m_resources = []
        m2m_dehydrated = []

        # TODO: Also model-specific and leaky. Relies on there being a
        # ``Manager`` there.
        the_m2ms_list = the_m2ms.all()
        if self.filter:
            the_m2ms_list = the_m2ms_list.filter(**filter)
        if self.limit:
            the_m2ms_list = the_m2ms_list[0:self.limit]

        for m2m in the_m2ms_list:
            m2m_resource = self.get_related_resource(m2m)
            m2m_bundle = Bundle(obj=m2m, request=bundle.request)
            self.m2m_resources.append(m2m_resource)
            m2m_dehydrated.append(self.dehydrate_related(m2m_bundle, m2m_resource, for_list=for_list))

        return m2m_dehydrated