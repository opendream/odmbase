# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib.auth import authenticate, logout
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.utils.http import urlsafe_base64_decode

from django.core.urlresolvers import NoReverseMatch, reverse, resolve, Resolver404, get_script_prefix

from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie import http
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError, HydrationError, InvalidSortError, ImmediateHttpResponse, Unauthorized
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.models import ApiKey, create_api_key
from tastypie.resources import ModelResource, BaseModelResource, sanitize
from tastypie.utils import trailing_slash
from django.contrib.auth import get_user_model

from social_auth.backends.facebook import BACKENDS as FACEBOOK_BACKENDS
from social_auth.backends.google import BACKENDS as GOOGLE_BACKENDS
from social_auth.backends.twitter import BACKENDS as TWITTER_BACKENDS

from odmbase.api.fields import SorlThumbnailField

from odmbase.common.api import ImageAttachResource, CommonResource, CommonAnonymousPostApiKeyAuthentication, \
    VerboseSerializer, CommonModelResource, CommonAuthorization, CommonAnonymousPostAuthorization, \
    CommonApiKeyAuthentication

from odmbase.common.constants import STATUS_PUBLISHED


BACKENDS = {}
BACKENDS.update(FACEBOOK_BACKENDS)
BACKENDS.update(GOOGLE_BACKENDS)
BACKENDS.update(TWITTER_BACKENDS)

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

    get_image = fields.FileField(attribute='get_image', readonly=True)

    is_new = fields.CharField(attribute='is_new', null=True, readonly=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authorization = CommonAnonymousPostAuthorization()
        authentication = CommonAnonymousPostApiKeyAuthentication()
        always_return_data = True
        detail_uri_name = 'username'
        include_absolute_url = True
        #excludes = ['password']
        filtering = {
            'username': ALL,
            'id': ALL,
            'email': ALL
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
            url(r'^(?P<resource_name>%s)/change_password%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('change_password'), name='api_change_password'),
            url(r'^(?P<resource_name>%s)/forgot_password%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('forgot_password'), name='api_forgot_password'),
            url(r'^(?P<resource_name>%s)/reset_password%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reset_password'), name='api_reset_password'),
        ]

    def _login(self, request, user):

        if user:
            if user.status == STATUS_PUBLISHED:
                # login(request, user)

                try:
                    key = ApiKey.objects.get(user=user)
                except ApiKey.DoesNotExist:
                    return self.create_response(
                        request, {
                            'error': 'The email you entered does not belong to any account.',
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
                        'error': 'Your account disabled. Please, contact administrator',
                    },
                    HttpForbidden,
                )
        else:
            return self.create_response(
                request, {
                    'error': 'The password you entered is incorrect. Please try again.',
                    'skip_login_redir': True,
                },
                HttpUnauthorized,
            )

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

        email = data.get('email', '') or data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=email, password=password)

        return self._login(request, user)

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

        print request.user

        if not request.user or (request.user and request.user.is_anonymous()):
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

    # TODO: not implement just implement like reset_password
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

    def change_password(self, request, **kwargs):
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

        data = self.deserialize(request, request.body)
        if data.get('token') and default_token_generator.check_token(request.user, data['token']):
            pass
        elif not request.user.check_password(data['old_password']):
            data = {"error": sanitize({'old_password': 'รหัสผ่านปัจจุบันไม่ถูกต้อง'})}
            return self.error_response(request, data, response_class=HttpForbidden)

        request.user.set_password(data['new_password'])
        request.user.save()

        bundle = self.build_bundle(obj=request.user, request=request)
        bundle = self.full_dehydrate(bundle)

        self.log_throttled_access(request)

        return self.create_response(request, bundle)

    def forgot_password(self, request, **kwargs):

        self.method_check(request, allowed=['post'])
        #self.is_authenticated(request)
        #self.throttle_check(request)

        data = self.deserialize(request, request.body)

        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email=data['email'])
        except User.DoesNotExist:
            data = {"error": sanitize({'email': 'อีเมลที่คุณกรอก ยังไม่มีอยู๋ในระบบ'})}
            return self.error_response(request, data, response_class=HttpForbidden)

        user.send_email_confirm()

        bundle = self.build_bundle(obj=user, request=request)
        bundle = self.full_dehydrate(bundle)

        #self.log_throttled_access(request)
        return self.create_response(request, bundle)

    def reset_password(self, request, **kwargs):

        self.method_check(request, allowed=['post'])
        # self.is_authenticated(request)
        #self.throttle_check(request)

        data = self.deserialize(request, request.body)
        UserModel = get_user_model()

        try:
            uid_int = urlsafe_base64_decode(data['uid'])

            user = UserModel.objects.get(id=uid_int)
        except (ValueError, UserModel.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, data['token']):

            return self._login(request, user)

        else:
            data = {"error": "ลิงก์ไม่ถูกต้อง"}
            return self.error_response(request, data, response_class=HttpForbidden)



# Simplify fields or user resource
class UserReferenceResource(UserResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        detail_uri_name = 'username'
        authentication = Authentication()
        serializer = VerboseSerializer(formats=['json'])
        #TODO: remove email field when upload image complete
        include_absolute_url = True

        fields = ['id', 'unicode_string', 'username',
                  'image', 'image_thumbnail_1x', 'image_thumbnail_2x', 'image_thumbnail_3x']
        allowed_methods = ['get', 'post'],
        filtering = {
            'username': ALL,
            'id': ALL
        }

    # Fix find resource uri: '/api/v1/user/username1/' --> 'username1/' wrong
    # Solution find resource uri: '/api/v1/user/username1/' --> 'user/username1/' true
    # remove rfind change to split '/' find uri
    def get_via_uri(self, uri, request=None):
        prefix = get_script_prefix()
        chomped_uri = uri

        if prefix and chomped_uri.startswith(prefix):
            chomped_uri = chomped_uri[len(prefix)-1:]

        split_chomped_uri_words =  chomped_uri.split('/')

        found_at = 0
        for word in split_chomped_uri_words:
            found_at = found_at + len(word)
            if word == self._meta.resource_name:
                break

        if found_at == len(chomped_uri):
            raise NotFound("An incorrect URL was provided '%s' for the '%s' resource." % (uri, self.__class__.__name__))
        
        chomped_uri = chomped_uri[found_at-1:]

        try:
            for url_resolver in getattr(self, 'urls', []):
                result = url_resolver.resolve(chomped_uri)

                if result is not None:
                    view, args, kwargs = result
                    break
            else:
                raise Resolver404("URI not found in 'self.urls'.")
        except Resolver404:
            raise NotFound("The URL provided '%s' was not a link to a valid resource." % uri)

        bundle = self.build_bundle(request=request)
        return self.obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))


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
            kwargs['created_by__id'] = bundle.request.user.id

        return super(AutoFilterCreatedByMixinResource, self).obj_get_list(bundle, **kwargs)


class SocialSignResource(ImageAttachResource, CommonModelResource):

    get_full_name = fields.CharField(attribute='get_full_name', null=True, readonly=True)
    get_short_name = fields.CharField(attribute='get_short_name', null=True, readonly=True)

    class Meta:
        queryset = User.objects.all()
        allowed_methods = ['post']
        authorization = CommonAnonymousPostAuthorization()
        authentication = CommonAnonymousPostApiKeyAuthentication()
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
                create_api_key(User, instance=user, created=True)
                key = ApiKey.objects.get(user=user)


            bundle.data['key'] = key.key
            bundle.data['is_new'] = user.is_new

            return bundle
        else:
            raise BadRequest("Error authenticating user with this provider")
