
import json
from uuid import uuid1

from django.db import models
from django.utils.translation import ugettext_lazy as _

from odmbase.common.models import AbstractPriorityModel


def get_upload_path(instance, filename):
    try:
        id = instance.attach_to.id
    except:
        id = 0

    filename = '%s.%s' % (str(uuid1()), filename.split('.')[-1])
    return 'common/%d/%s' % (id, filename)


class Image(AbstractPriorityModel):
    attach_to = models.ForeignKey('common.CommonModel', null=True, blank=True)
    image = models.ImageField(upload_to=get_upload_path)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['ordering']

    def __unicode__(self):
        return self.title

    def unicode_string(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        if not self.title and self.image:
            self.title = ' '.join(self.image.name.split('.')[0:-1])

        super(Image, self).save(*args, **kwargs)

    def user_can_edit(self, user):
        return not self.attach_to or self.attach_to.cast().user_can_edit(user)


class YoutubeLinkMixin(models.Model):
    youtube_url = models.URLField(verbose_name=_('Youtube url'), blank=True, null=True)
    youtube_id = models.CharField(max_length=25, verbose_name=_('Youtube id'), blank=True, null=True)

    class Meta:
        abstract = True


class WebsiteMixin(models.Model):
    website_url = models.URLField(max_length=512, verbose_name=_('Website url'), blank=True, null=True)
    website_meta = models.TextField(verbose_name=_('Website meta'), blank=True, null=True)

    class Meta:
        abstract = True

    def get_website_meta(self):
        if self.website_meta:
            return json.loads(self.website_meta)
        return {}


class QuoteMixin(models.Model):
    quote = models.TextField(verbose_name=_('Quote'), blank=True, null=True)

    class Meta:
        abstract = True
