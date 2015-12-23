from django.conf import settings
from django.db import models
from odmbase.common.models import CommonModel


class PrivateMessage(CommonModel):
    CREATED_BY_FIELD = 'src'

    src = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_message_src')
    dst = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_message_dst')

    title = models.CharField(max_length=512, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Cro'
        # return '%s message: "%s"' % (self.src.get_full_name(), self.message)