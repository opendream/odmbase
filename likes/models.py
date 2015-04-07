
from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from django.utils.translation import ugettext_lazy as _

from odmbase.common.models import CommonModel


class Like(CommonModel):
    CREATED_BY_FIELD = 'src'

    src = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Created by'), related_name='user_likes')
    dst = models.ForeignKey(CommonModel, verbose_name=_('Destination'), related_name='likes')

    #created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)

    def __unicode(self):
        return '%s liked: "%s"' % (self.src.get_full_name(), self.message)

    def save(self, commit=True, *args, **kwargs):
        if not self.pk:
            try:
                self.pk = Like.objects.get(src=self.src, dst=self.dst).pk
            except Like.DoesNotExist:
                pass
        super(Like, self).save(*args, **kwargs)

    @property
    def get_dst(self):
        return self.dst and self.dst.cast()
        

@receiver([post_save, post_delete], sender=Like)
def update_likes_count(sender, instance, **kwargs):
    if kwargs.get('signal') == post_delete or kwargs.get('created') or instance.is_deleted:
        goal = instance.dst.cast()
        try:
            likes_count = goal.likes_count
            likes_count = Like.objects.filter(dst=goal.commonmodel_ptr).count()
            goal.likes_count = likes_count
        except:
            pass
        else:
            goal.save()

