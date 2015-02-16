from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect

from django.utils.http import urlsafe_base64_decode



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

