from django.db import models
from django.utils.translation import ugettext_lazy as _
from odmbase.account.models import User as ODMUser


class User(ODMUser):

    pass
    #description = models.TextField(verbose_name=_('About you'), null=True, blank=True)
    #address = models.TextField(verbose_name=_('Address'), null=True, blank=True)
    #phone = models.CharField(verbose_name=_('Phone'), max_length=255, null=True, blank=True)
