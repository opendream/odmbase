
from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from odmbase.common.models import CommonModel, CommonTrashReasonMixin


class Comment(CommonModel, CommonTrashReasonMixin):
    CREATED_BY_FIELD = 'src'

    src = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Created by'), related_name='user_comments')
    dst = models.ForeignKey(CommonModel, verbose_name=_('Destination'), related_name='comments')

    message = models.TextField(verbose_name=_('Comment'), null=True, blank=True)
    #created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)

    def __unicode(self):
        return '%s commented: "%s"' % (self.src.get_full_name(), self.message)

    @property
    def get_dst(self):
        return self.dst and self.dst.cast()


@receiver([post_save, post_delete], sender=Comment)
def update_comments_count(sender, instance, **kwargs):
    if kwargs.get('signal') == post_delete or kwargs.get('created') or instance.is_deleted:
        goal = instance.dst.cast()
        try:
            comments_count = goal.comments_count
            comments_count = Comment.objects.filter(dst=goal.commonmodel_ptr).count()
            goal.comments_count = comments_count
        except:
            pass
        else:
            goal.save()


