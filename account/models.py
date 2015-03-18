import time
import re
from uuid import uuid1

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from tastypie.models import create_api_key

from odmbase.account.functions import rewrite_username
from odmbase.common.constants import STATUS_CHOICES, STATUS_PUBLISHED, STATUS_PENDING
from odmbase.common.models import CommonModel
from odmbase.common.storage import OverwriteStorage

'''
field_extend = models.Model
try:
    from account.models import AbstractAccountField
    field_extend = AbstractAccountField
except ImportError:
    pass
'''

def get_upload_path(instance, filename):
    return 'user/%d/avatar-%d.%s' % (instance.id, int(time.time()), filename.split('.')[-1])

class AbstractPeopleField(models.Model):

    priority = models.PositiveIntegerField(default=0)
    ordering = models.PositiveIntegerField(null=True, blank=True)

    image = models.ImageField(verbose_name=_('Avartar'), null=True, blank=True, upload_to=get_upload_path, storage=OverwriteStorage())
    # Internal
    first_name = models.CharField(verbose_name=_('First name'), max_length=255, null=True, blank=True)
    last_name = models.CharField(verbose_name=_('Last name'), max_length=255, null=True, blank=True)



    class Meta:
        abstract = True


    def get_full_name(self):
        try:
            full_name = '%s %s' % (self.first_name or '', self.last_name or '')
            return full_name.strip()
        except:
            return ''

    def get_short_name(self):
        output = ''
        try:
            if self.first_name.strip() and self.last_name.strip():
                output = '%s.%s' % (self.first_name.strip(), self.last_name.strip()[0])

            elif self.first_name.strip():
                output = self.first_name.strip()

            elif self.last_name.strip():
                output = self.last_name.strip()

            output = ''
        except:
            output = ''

        if not output:
            output = self.username

        return output

    def get_display_name(self, allow_email=False):
        if allow_email:
            return self.get_full_name() or self.email or self.username

        return self.get_full_name() or self.username


    def __unicode__(self):
        return self.get_display_name()




class User(AbstractPeopleField, CommonModel, AbstractBaseUser, PermissionsMixin):

    STATUS_PUBLISHED = STATUS_PUBLISHED
    STATUS_PENDING = STATUS_PENDING

    username = models.CharField(_('Username'), max_length=30, unique=True,
        help_text=_('Required 30 characters or fewer. Letters, numbers and @/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
    ])

    email = models.EmailField(
        verbose_name=_('Email address'),
        max_length=255,
        unique=True,
    )

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # Deprecated

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):

        super(User, self).__init__(*args, **kwargs)
        password_field = self._meta.get_field_by_name('password')[0]
        password_field.blank = True
        password_field.null = True

    def __unicode__(self, allow_email=False):
        if allow_email:
            return self.get_full_name() or self.email or self.username

        return self.get_full_name() or self.username

    def save(self, commit=True, force_insert=False, force_update=False, *args, **kwargs):

        if not self.username:
            self.username = rewrite_username(self.email)

        password = self.password
        is_new = self.pk is None

        # WTF Django security

        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        elif self.id and not self.password:

            from account.models import User as AccountUser
            user = AccountUser.objects.get(id=self.id)

            if user.password:
                self.password = user.password

        elif is_new:
            self.set_password(str(uuid1())[0: 10].replace('-', ''))


        if is_new and settings.REGISTER_CONFIRM:
            self.status = STATUS_PENDING


        super(User, self).save(*args, **kwargs)

        if is_new and self.id:
            # For api login
            create_api_key(self.__class__, instance=self, created=True)
            if not password:
                self.send_email_confirm(
                    email_template_name='account/email/register_email.html',
                    subject_template_name='account/email/register_email_subject.txt'
                )

    # play safe for original django models check active
    @property
    def is_active(self):
        return self.status == STATUS_PUBLISHED

    def get_full_name(self):
        try:
            full_name = '%s %s' % (self.first_name or '', self.last_name or '')
            return full_name.strip()
        except:
            return ''

    def get_short_name(self):
        output = ''
        try:
            if self.first_name.strip() and self.last_name.strip():
                output = '%s.%s' % (self.first_name.strip(), self.last_name.strip()[0])

            elif self.first_name.strip():
                output = self.first_name.strip()

            elif self.last_name.strip():
                output = self.last_name.strip()

        except:
            output = ''

        if not output:
            output = self.username

        return output

    def user_can_edit(self, user):
        return self == user

    def send_email_confirm(self, subject_template_name='account/email/password_reset_email_subject.txt',
                           email_template_name='account/email/password_reset_email.html',
                           use_https=False, token_generator=default_token_generator,
                           from_email=None, request=None, html_email_template_name=None, check_is_active=True):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail

        UserModel = get_user_model()
        email = self.email
        params = {'email__iexact': email}
        if check_is_active:
            params['status'] = STATUS_PUBLISHED

        active_users = UserModel._default_manager.filter(**params)
        for user in active_users:

            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable

            if False and not user.has_usable_password():
                continue

            domain = settings.SITE_DOMAIN
            site_name = settings.SITE_NAME

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
