import pytz

from django.conf import settings
from django.db import models

from django.utils.timezone import make_naive
from django.utils.translation import ugettext_lazy as _

from odmbase.common.models import CommonModel, CommonTrashReasonMixin

HAS_FEED_INTEGRATION = True
try:
    from notification_feeds.feed_managers import manager
except:
    HAS_FEED_INTEGRATION = False

class Comment(CommonModel, CommonTrashReasonMixin):
    CREATED_BY_FIELD = 'src'

    src = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Created by'), related_name='user_comments')
    dst = models.ForeignKey(CommonModel, verbose_name=_('Destination'), related_name='comments')

    message = models.TextField(verbose_name=_('Comment'), null=True, blank=True)
    #created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)

    def __unicode__(self):
        return '%s commented: "%s"' % (self.src.get_full_name(), self.message)

    def save(self, commit=True, *args, **kwargs):
        is_new = self.pk is None
        super(Comment, self).save(*args, **kwargs)


        # update comments count
        instance = self.dst.cast()
        if hasattr(instance, 'comments_count'):
            comments_count = Comment.objects.filter(dst=instance.commonmodel_ptr).count()
            instance.comments_count = comments_count
            instance.save()
        
        # add to redis feed
        if HAS_FEED_INTEGRATION:
            is_created_by = self.src.id == self.dst.common_created_by.id

            if is_new and not is_created_by:
                manager.add_item(self)


    def delete(self, using=None):
        super(Comment, self).delete(using)

        # REMOVE FROM REDIS
        if HAS_FEED_INTEGRATION:
            manager.remove_item(self)

    @property
    def get_dst(self):
        return self.dst and self.dst.cast()

    def create_activity(self, item_id=None, method=None, extra_context=None):

        from notification_feeds.verbs import CommentVerb
        from notification_feeds.activities import Activity

        extra_context = extra_context or {}
        activity = Activity(
            actor = self.src.id,
            verb = CommentVerb,
            object = self.id,
            target = self.get_dst.id,
            time = make_naive(self.created, pytz.utc),
            extra_context = extra_context
        )
        return activity


