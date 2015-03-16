from django.conf.urls import url
from django.contrib.auth import authenticate, logout
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.utils.http import urlsafe_base64_decode
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.exceptions import BadRequest
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.models import ApiKey, create_api_key
from tastypie.resources import ModelResource, BaseModelResource
from tastypie.utils import trailing_slash
from django.contrib.auth import get_user_model

from social_auth.backends.facebook import BACKENDS

from odmbase.common.api import ImageAttachResource, CommonResource, CommonAnonymousPostApiKeyAuthentication, \
    VerboseSerializer, CommonModelResource

from odmbase.common.constants import STATUS_PUBLISHED


User = get_user_model()

# post image
# curl -F "image=@hipster.png" localhost:8000/api/v1/user/87/set_image/

class UserResource(ImageAttachResource, CommonModelResource):

    STATUS_PUBLISHED = fields.IntegerField(attribute='STATUS_PUBLISHED')
    STATUS_PENDING = fields.IntegerField(attribute='STATUS_PENDING')
    #password = fields.CharField(attribute='password', null=True)
    username = fields.CharField(attribute='username')

    get_full_name = fields.CharField(attribute='get_full_name', null=True, readonly=True)
    get_short_name = fields.CharField(attribute='get_short_name', null=True, readonly=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authentication = CommonAnonymousPostApiKeyAuthentication()
        always_return_data = True
        detail_uri_name = 'username'
        #excludes = ['password']
        filtering = {
            'username': ALL
        }

    def prepend_urls(self):
        return super(UserResource, self).prepend_urls() + [

            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/me%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('me'), name='api_me'),
            url(r'^(?P<resource_name>%s)/register_confirm%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('register_confirm'), name='api_register_confirm'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

        email = data.get('email', '') or data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=email, password=password)
        if user:
            if user.status == STATUS_PUBLISHED:
                #login(request, user)

                try:
                    key = ApiKey.objects.get(user=user)
                except ApiKey.DoesNotExist:
                    return self.create_response(
                        request, {
                            'error': 'Missing key',
                        },
                        HttpForbidden,
                    )

                ret = self.create_response(request, {
                    'success': True,
                    'username': user.username,
                    'key': key.key
                })

                return ret
            else:
                return self.create_response(
                    request, {
                        'error': 'Your account disabled',
                    },
                    HttpForbidden,
                )
        else:
            return self.create_response(
                request, {
                    'error': 'invalid login',
                    'skip_login_redir': True,
                },
                HttpUnauthorized,
            )

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {'success': False}, HttpUnauthorized)

    def me(self, request, **kwargs):

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if not request.user:
            return self.create_response(
                request, {
                    'error': 'You are anonymous user',
                },
                HttpForbidden,
            )

        bundle = self.build_bundle(obj=request.user, request=request)
        bundle = self.full_dehydrate(bundle)

        self.log_throttled_access(request)

        return self.create_response(request, bundle)

    def register_confirm(self, request, ** kwargs):

        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

        uidb64 = data.get('uidb64', '')
        token = data.get('token', '')



        try:
            uid_int = urlsafe_base64_decode(uidb64)
            user = User.objects.get(id=uid_int)
        except (ValueError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.status = STATUS_PUBLISHED
            user.save()

            try:
                key = ApiKey.objects.get(user=user)
            except ApiKey.DoesNotExist:
                return self.create_response(
                    request, {
                        'error': 'Missing key',
                    },
                    HttpForbidden,
                )
            #user_authen = authenticate(username=user.username, ignore_password=True)
            #login(request, user_authen)
            return self.create_response(request, {
                'success': True,
                'username': user.username,
                'key': key.key
            })

        else:
            return self.create_response(
                request, {
                    'error': 'invalid link',
                    'skip_login_redir': True,
                },
                HttpUnauthorized,
            )

models.signals.post_save.connect(create_api_key, sender=User)

# Simplify fields or user resource
class UserReferenceResource(UserResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        detail_uri_name = 'username'
        authentication = Authentication()
        serializer = VerboseSerializer(formats=['json'])
        #TODO: remove email field when upload image complete
        fields = ['unicode_string', 'username',
                  'image', 'image_thumbnail_1x', 'image_thumbnail_2x', 'image_thumbnail_3x']
        allowed_methods = ['get'],
        filtering = {
            'username': ALL,
            'id': ALL
        }


class AutoAssignCreatedByMixinResource(ModelResource):

    created_by = fields.ForeignKey(UserReferenceResource, 'created_by', full=True)

    def obj_create(self, bundle, **kwargs):
        bundle.data['created_by'] = bundle.request.user
        return super(AutoAssignCreatedByMixinResource, self).obj_create(bundle, **kwargs)


    def obj_update(self, bundle, skip_errors=False, **kwargs):
        try:
            del (bundle.data['created_by'])  # Prevent change created by from client
        except:
            pass

        return super(AutoAssignCreatedByMixinResource, self).obj_update(bundle, skip_errors=False, **kwargs)


class AutoFilterCreatedByMixinResource(ModelResource):

    created_by = fields.ForeignKey(UserReferenceResource, 'created_by', full=True)

    def obj_get_list(self, bundle, **kwargs):
        if not kwargs.get('created_by'):
            kwargs['created_by'] = bundle.request.user.id

        return super(AutoFilterCreatedByMixinResource, self).obj_get_list(bundle, **kwargs)


class SocialSignResource(ImageAttachResource, CommonModelResource):

    get_full_name = fields.CharField(attribute='get_full_name', null=True, readonly=True)
    get_short_name = fields.CharField(attribute='get_short_name', null=True, readonly=True)

    class Meta:
        queryset = User.objects.all()
        allowed_methods = ['post']
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        serializer = VerboseSerializer(formats=['json'])
        excludes = ['password']
        resource_name = 'social_sign'
        return_resource = UserResource


    def obj_create(self, bundle, **kwargs):

        provider = bundle.data['provider']
        access_token = bundle.data['access_token']

        Backend = BACKENDS[provider]
        backend = Backend(request=bundle.request, redirect='/')


        user = backend.do_auth(access_token)
        if user and user.is_active:
            bundle.obj = user

            try:
                key = ApiKey.objects.get(user=user)
            except ApiKey.DoesNotExist:
                raise HttpForbidden

            bundle.data['key'] = key.key

            return bundle
        else:
            raise BadRequest("Error authenticating user with this provider")
