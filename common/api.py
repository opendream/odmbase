import json
import ast

from django.conf import settings
from django.conf.urls import url
from django.core.exceptions import ValidationError
from django.utils.cache import patch_vary_headers, patch_cache_control
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest
from tastypie.http import HttpForbidden
from tastypie.resources import ModelResource, csrf_exempt, sanitize
from tastypie.serializers import Serializer
from tastypie import http
from tastypie import fields
from django.core.serializers import json as djangojson
from tastypie.utils import trailing_slash
from odmbase.api.fields import SorlThumbnailField

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
    def check_active(self, user):
        if not self.require_active:
            # Ignore & move on.
            return True

        return user.status == user.STATUS_PUBLISHED

    def is_authenticated(self, request, **kwargs):

        key_auth_check = super(CommonApiKeyAuthentication, self).is_authenticated(request, **kwargs)

        if request.method == 'GET' or key_auth_check:
            return True

        return key_auth_check

class CommonAnonymousPostApiKeyAuthentication(CommonApiKeyAuthentication):

    def is_authenticated(self, request, **kwargs):

        if request.method in ['GET', 'POST'] and len(request.path.split('/')) == 3:
            return True
        else:
            return super(CommonAnonymousPostApiKeyAuthentication, self).is_authenticated(request, **kwargs)

    def get_identifier(self, request):

        if request.method in ['GET', 'POST'] and len(request.path.split('/')) == 3:
            return "%s_%s" % (request.META.get('REMOTE_ADDR', 'noaddr'), request.META.get('REMOTE_HOST', 'nohost'))
        else:
            return super(CommonAnonymousPostApiKeyAuthentication, self).get_identifier(request)



class CommonResource(ModelResource):

    unicode_string = fields.CharField(attribute='unicode_string', null=True, blank=True)

    class Meta:
        queryset = CommonModel.objects.all()
        resource_name = 'common'
        authorization = Authorization()
        always_return_data = True
        serializer = VerboseSerializer(formats=['json'])

    def build_schema(self):
        base_schema = super(CommonResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
            if f.name in base_schema['fields'] and f.choices:
                base_schema['fields'][f.name].update({
                    'choices': f.choices,
                })
        return base_schema

    def dehydrate(self, bundle):

        # TODO: implement me
        bundle.data['can_edit'] = True
        return bundle

    def put_detail(self, request, **kwargs):
        if not request.META.get('CONTENT_TYPE', 'application/json').startswith('application/json') and not hasattr(request, '_body'):
            request._body = ''

        return super(CommonResource, self).put_detail(request, **kwargs)

    def deserialize(self, request, data, format=None):

        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        if format == 'application/x-www-form-urlencoded':
            return request.POST

        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)

            return data

        return super(CommonResource, self).deserialize(request, data, format)

    def get_resource_uri(self, bundle_or_obj=None, url_name='api_dispatch_list'):

        resource_uri = super(CommonResource, self).get_resource_uri(bundle_or_obj, url_name)

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


class ImageAttachResource(ModelResource):

    image = fields.FileField(attribute='image', null=True, blank=True)

    def prepend_urls(self):
        print self._meta.resource_name
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/set_image%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('set_image'), name="api_set_image"),
        ]


    def set_image(self, request=None, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

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
class ImageResource(CommonResource):

    attach_to = fields.ForeignKey(CommonResource, 'attach_to', null=True, blank=True)
    image = fields.FileField(attribute='image')
    image_thumbnail_product_front = SorlThumbnailField(attribute='image', thumb_options={'geometry': '280x280'})
    image_thumbnail_1x = SorlThumbnailField(attribute='image', thumb_options={'geometry': '400x400'})
    image_thumbnail_2x = SorlThumbnailField(attribute='image', thumb_options={'geometry': '800x800'})
    image_thumbnail_3x = SorlThumbnailField(attribute='image', thumb_options={'geometry': '1024x1024'})

    unicode_string = fields.CharField(attribute='unicode_string', null=True, blank=True)

    class Meta:
        queryset = Image.objects.all()
        resource_name = 'image'
        #authentication = CommonApiKeyAuthentication() # Todo: uncomment this line
        authorization = Authorization()
        always_return_data = True
        serializer = VerboseSerializer(formats=['json'])

