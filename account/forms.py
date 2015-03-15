from uuid import uuid1

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from odmbase.account.functions import rewrite_username


class EmailAuthenticationForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    remember_me = forms.NullBooleanField()

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')


        if email and password:
            self.user_cache = authenticate(username=email, password=password)

            if self.user_cache is None:
                raise forms.ValidationError(_('Please, enter correct email/username and password.'))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_('This account not activated.'))

        return self.cleaned_data


    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=80)

    check_is_active = True

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        params = {'email__iexact': email}
        if self.check_is_active:
            params['is_active'] = True

        active_users = UserModel._default_manager.filter(**params)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable

            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)

            if html_email_template_name:
                html_email = loader.render_to_string(html_email_template_name, c)
            else:
                html_email = None
            send_mail(subject, email, from_email, [user.email], html_message=html_email)


class ResetPasswordForm(PasswordResetForm):

    check_is_active = False

    def clean_email(self):

        email = self.cleaned_data.get('email')

        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise forms.ValidationError(_('Your email address is not registered.'))

        if not user.is_active:
            #raise forms.ValidationError(_('Your email address is not activated.'))
            pass

        return email


class InviteForm(PasswordResetForm):

    check_is_active = False

    def clean_email(self):

        email = self.cleaned_data.get('email')

        UserModel = get_user_model()

        try:
            UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            password = str(uuid1())[0: 10].replace('-', '')

            username = rewrite_username(email)

            if len(username) > 30:
                raise forms.ValidationError(
                    _('Ensure this email prefix(characters before @) has at most 30 characters '))

            user = UserModel.objects.create(username=username, email=email, is_active=False)
            user.set_password(password)
            user.save()

        return email


class AccountEditForm(forms.Form):

    username    = forms.CharField(max_length=30)
    email       = forms.EmailField(max_length=75)
    password    = forms.CharField(required=False, max_length=128, widget=forms.PasswordInput())
    password2   = forms.CharField(required=False, max_length=128, widget=forms.PasswordInput())
    first_name  = forms.CharField(required=False, max_length=30, widget=forms.TextInput())
    last_name   = forms.CharField(required=False, max_length=30, widget=forms.TextInput())

    description = forms.CharField(required=False, widget=forms.Textarea())

    # Taxonomy
    #user_roles = forms.ModelMultipleChoiceField(required=False, queryset=UserRole.objects.all(), widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_user_roles'}))


    PERMALINK_FIELDS = ['username', 'email']

    def __init__(self, inst=None, model=None, required_password=False, *args, **kwargs):
        super(AccountEditForm, self).__init__(inst, model, *args, **kwargs)

        self.inst = inst

        if required_password:
            self.fields['password'].required = True
            self.fields['password2'].required = True

    def clean_password2(self):
        password = self.cleaned_data.get('password', '')
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise forms.ValidationError(_('Password mismatch.'))
        return password2


class AccountRegisterForm(PasswordResetForm):

    check_is_active = False

    def clean_email(self):

        email = self.cleaned_data.get('email')

        UserModel = get_user_model()

        try:
            UserModel.objects.get(email=email, is_active=True)
            raise forms.ValidationError(_('This email is already in use.')) 
        except UserModel.DoesNotExist:

            password = str(uuid1())[0: 10].replace('-', '')

            try:
                UserModel.objects.get(email=email)

            except UserModel.DoesNotExist:

                username = rewrite_username(email)

                if len(username) > 30:
                    raise forms.ValidationError(_('Ensure this email prefix(characters before @) has at most 30 characters '))

                user = UserModel.objects.create(username=username, email=email, is_active=False)
                user.set_password(password)
                user.save()


        return email


class UserCreationForm(DjangoUserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    DjangoUserCreationForm.error_messages.update({
        'duplicate_email': _("A user with that email already exists."),
    })

    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        UserModel = get_user_model()
        username = self.cleaned_data["username"]
        try:
            UserModel._default_manager.get(username=username)
        except UserModel.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    def clean_email(self):
        # Since User.email is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        try:
            UserModel._default_manager.get(email=email)
        except UserModel.DoesNotExist:
            return email
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )


class UserChangeForm(DjangoUserChangeForm):
    class Meta:
        model = get_user_model()
        fields = []
