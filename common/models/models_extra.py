
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from math import log

epoch = datetime(1970, 1, 1)
def epoch_seconds(date):
    """Returns the number of seconds from the epoch to date."""
    td = date - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)


class HotScoreMixin(models.Model):
    hot_score = models.FloatField(verbose_name=_('Hot Score'), default=0, blank=True)

    class Meta:
        abstract = True

    def update_hot_score(self, score, date, extra=0, commit=True):

        # Reddis algorithm ** 
        # ref: https://moz.com/blog/reddit-stumbleupon-delicious-and-hacker-news-algorithms-exposed
        
        order = log(max(abs(score), 1), 10)
        sign = 1 if score > 0 else -1 if score < 0 else 0

        #date = self.created #comment this line if use activity date na

        date = date.replace(tzinfo=None)
        seconds = epoch_seconds(date) - 1134028003

        second_constant = settings.HOT_SCORE_SECOND_CONSTANT
        
        # (sign * seconds / (30 * 86400)) = popular in 30 days
        self.hot_score = round(order + (sign * seconds / second_constant) + extra, 7)
        if commit:
            self.save()
