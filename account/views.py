from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render

from django.utils.http import urlsafe_base64_decode
from oauth2 import Consumer as OAuthConsumer, Token
from urllib2 import Request, HTTPError

# deprecate when angular implement from api
from django.views.decorators.csrf import csrf_exempt
from social_auth.decorators import dsa_view
from social_auth.exceptions import AuthTokenError
from social_auth.views import associate_complete, complete_process
from odmbase import settings


def account_register_confirm(request, uidb64=None, token=None, email_setting=False):

    UserModel = get_user_model()

    try:
        uid_int = urlsafe_base64_decode(uidb64)

        user = UserModel.objects.get(id=uid_int)
    except (ValueError, UserModel.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        user_authen = authenticate(username=user.username, ignore_password=True)
        auth_login(request, user_authen)
        return redirect(reverse('account_edit') + '?reset_password=True')
    else:
        return HttpResponse('invalid link', status=404)

def account_reset_password(request, uidb64=None, token=None, email_setting=False):

    UserModel = get_user_model()

    try:
        uid_int = urlsafe_base64_decode(uidb64)

        user = UserModel.objects.get(id=uid_int)
    except (ValueError, UserModel.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        user_authen = authenticate(username=user.username, ignore_password=True)
        auth_login(request, user_authen)
        return redirect(reverse('account_edit') + '?reset_password=True')
    else:
        return HttpResponse('invalid link', status=404)

# =========================================================
# Social Auth
# =========================================================

def login_facebook(request):
    if request.GET.get('next'):
        request.session['facebook_next'] = request.GET.get('next')

    from social_auth.views import auth
    return auth(request, 'facebook')

def login_facebook_redirect(request):
    if request.session.get('facebook_next'):
        url = request.session.get('facebook_next')
    else:
        url = settings.LOGIN_REDIRECT_URL

    return redirect(url)

def login_twitter(request):
    if request.GET.get('next'):
        request.session['twitter_next'] = request.GET.get('next')

    from social_auth.views import auth
    return auth(request, 'twitter')

@csrf_exempt
@dsa_view()
def complete(request, backend, *args, **kwargs):

    print 'pppppppp'
    # Multiple unauthorized tokens are supported (see #521)
    name = 'twitter' + 'unauthorized_token_name'
    token = None
    unauthed_tokens = request.session.get(name) or []
    if not unauthed_tokens:
        raise AuthTokenError(None, 'Missing unauthorized token')
    for unauthed_token in unauthed_tokens:
        token = Token.from_string(unauthed_token)

        if token.key == request.REQUEST.get('oauth_token', 'no-token'):
            unauthed_tokens = list(set(unauthed_tokens) - set([unauthed_token]))
            request.session[name] = unauthed_tokens
            request.session.modified = True
            break
    else:
        raise AuthTokenError(None, 'Incorrect tokens')

    access_token = backend.access_token(token)
    print 'uuuuuuuuu'
    return render(request, 'account/oauth_sign.html', {'access_token': access_token})
