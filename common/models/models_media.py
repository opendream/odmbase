
from uuid import uuid1

from django.db import models
from django.utils.translation import ugettext_lazy as _


def get_upload_path(instance, filename):
    try:
        id = instance.attach_to.id
    except:
        id = 0

    filename = '%s.%s' % (str(uuid1()), filename.split('.')[-1])
    return 'common/%d/%s' % (id, filename)


class Image(models.Model):
    attach_to = models.ForeignKey(CommonModel, null=True, blank=True)
    image = models.ImageField(upload_to=get_upload_path)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    def unicode_string(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
        if not self.title and self.image:
            self.title = ' '.join(self.image.name.split('.')[0:-1])

        super(Image, self).save(*args, **kwargs)
