import pytz

from django.conf import settings
from django.db import models
from django.utils.timezone import make_naive
from django.utils.translation import ugettext_lazy as _


from odmbase.common.models import CommonModel

HAS_FEED_INTEGRATION = True
try:
    from notification_feeds.feed_managers import manager
except:
    HAS_FEED_INTEGRATION = False

class Like(CommonModel):
    CREATED_BY_FIELD = 'src'

    src = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Created by'), related_name='user_likes')
    dst = models.ForeignKey(CommonModel, verbose_name=_('Destination'), related_name='likes')

    #created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)

    def __unicode(self):
        return '%s liked: "%s"' % (self.src.get_full_name(), self.message)

    def save(self, commit=True, *args, **kwargs):
        is_new = self.pk is None
        if not self.pk:
            try:
                self.pk = Like.objects.get(src=self.src, dst=self.dst).pk
            except Like.DoesNotExist:
                pass
        super(Like, self).save(*args, **kwargs)

        instance = self.dst.cast()

        # Update likes count
        if hasattr(instance, 'likes_count'):
            likes_count = Like.objects.filter(dst=instance.commonmodel_ptr).count()
            instance.likes_count = likes_count
            instance.save()


        # add to redis feed
        if HAS_FEED_INTEGRATION:

            is_created_by = self.src.id == self.dst.common_created_by.id

            if is_new and not is_created_by:
                manager.add_item(self)

    def delete(self, using=None):
        super(Like, self).delete(using)

        # REMOVE FROM REDIS
        if HAS_FEED_INTEGRATION:
            manager.remove_item(self)

    @property
    def get_dst(self):
        return self.dst and self.dst.cast()

    def create_activity(self, item_id=None, method=None, extra_context=None):

        from notification_feeds.activities import Activity
        from notification_feeds.verbs import LikeVerb

        extra_context = extra_context or {}
        activity = Activity(
            actor = self.src.id,
            verb = LikeVerb,
            object = self.id,
            target = self.get_dst.id,
            time = make_naive(self.created, pytz.utc),
            extra_context = extra_context
        )
        return activity
