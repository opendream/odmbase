# -*- coding: utf-8 -*-

import copy
from uuid import uuid1
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
import bleach

import re


class CommonTrashManager(models.Manager):
    def filter_without_trash(self, *args, **kwargs):
        if not kwargs.get('is_deleted'):
            return super(CommonTrashManager, self).filter(*args, **kwargs).exclude(is_deleted=True)
        else:
            return super(CommonTrashManager, self).filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        if not kwargs.get('is_deleted'):
            return super(CommonTrashManager, self).exclude(*args, **kwargs).exclude(is_deleted=True)

    def filter(self, *args, **kwargs):
        return self.filter_without_trash(*args, **kwargs)

    def all(self, *args, **kwargs):
        return self.filter(*args, **kwargs)

    def get_without_trash(self, *args, **kwargs):
        if not kwargs.get('is_deleted'):
            kwargs['is_deleted'] = False
        return super(CommonTrashManager, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.get_without_trash(*args, **kwargs)

    def annotate(self, *args, **kwargs):
        return super(CommonTrashManager, self).exclude(is_deleted=True).annotate(*args, **kwargs)


class AbstractCommonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        self.full_clean()

        ALLOWED_TAGS = [
            'p', 'em', 'strong', 'span', 'a', 'br', 'strong', 'ul', 'ol', 'li', 'img',
            'h3', 'h4', 'h5', 'h6',
            'table', 'thead', 'tbody', 'tfoot', 'th', 'tr', 'td',
            's', 'u', 'iframe', 'embed', 'object'
        ]
        ALLOWED_ATTRIBUTES = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt', 'ta-insert-video', 'allowfullscreen', 'frameborder', 'style', 'class'],
            'iframe': ['src', 'allowfullscreen', 'frameborder', 'width', 'height']
        }

        for field in self._meta.fields:
            if type(field) in [models.fields.TextField]:
                value = bleach.clean(getattr(self, field.name), tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
                setattr(self, field.name, value)
            elif type(field) in [models.fields.CharField]:
                value = bleach.clean(getattr(self, field.name))
                setattr(self, field.name, value)

        super(AbstractCommonModel, self).save(*args, **kwargs)

    @property
    def inst_name(self):
        return self.__class__.__name__

    def unicode_string(self):
        return self.__unicode__()


class AbstractCommonTrashModel(AbstractCommonModel):
    is_deleted = models.BooleanField(default=False)
    objects = CommonTrashManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(AbstractCommonTrashModel, self).save(*args, **kwargs)

    def trash(self, *args, **kwargs):

        self.is_deleted = True

        deleted_uuid = str(uuid1())[0: 10].replace('-', '')
        if hasattr(self, 'permalink'):
            self.permalink = 'deleted_%s_%s' % (deleted_uuid, self.permalink)
        # Common for delete user
        if hasattr(self, 'username'):
            self.email = 'deleted_%s_%s' % (deleted_uuid, self.username)
        if hasattr(self, 'email'):
            self.email = 'deleted_%s_%s' % (deleted_uuid, self.email)

        self.save()
        return self

    def delete(self, *args, **kwargs):
        return self.trash(self, *args, **kwargs)

    def remove(self, *args, **kwargs):
        return super(AbstractCommonTrashModel, self).delete(*args, **kwargs)


class CommonTrashReasonMixin(models.Model):
    reason = models.TextField(verbose_name=_('Reason'), null=True, blank=True)

    class Meta:
        abstract = True


class AbstractCachedModel(models.Model):

    cached_vars = ['status']

    def __init__(self, *args, **kwargs):
        super(AbstractCachedModel, self).__init__(*args, **kwargs)
        self.var_cache = {}
        for var in self.cached_vars:
            try:
                self.var_cache[var] = copy.copy(getattr(self, var))
            except:
                self.var_cache[var] = None

    class Meta:
        abstract = True


class AbstractPermalink(AbstractCommonModel):

    permalink = models.CharField(max_length=255, unique=True,
        help_text=_('Required unique 30 characters or fewer. Letters, numbers and ./@/+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.+-]+$'), _('Enter a valid permalink.'), 'invalid')
        ])

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.permalink


class AbstractPriorityModel(models.Model):

    priority = models.PositiveIntegerField(default=0)
    ordering = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Logic make from "test_uptodate_status (domain.tests.test_model.TestStatement)"

        if not self.id:
            super(AbstractPriorityModel, self).save(*args, **kwargs)
            #instance = self.objects.get(id=self.id)
            self.save()
        else:
            self.ordering = int('%s%s' % (('0' * 2 + '%s' % self.priority)[-2:], ('0' * 8 + '%s' % self.id)[-8:]))
            super(AbstractPriorityModel, self).save(*args, **kwargs)


class AbstractAwesomeModel(AbstractCommonTrashModel, AbstractCachedModel):
    class Meta:
        abstract = True

    def user_can_edit(self, user):

        if user and user.is_authenticated() and user.is_staff:
            return True

        if hasattr(self, 'CREATED_BY_FIELD'):
            return (getattr(self, self.CREATED_BY_FIELD) == user)
        elif hasattr(self, 'created_by'):
            return (self.created_by == user)

        return False


class CommonModel(AbstractAwesomeModel):

    real_type = models.ForeignKey(ContentType, editable=False)

    def __unicode__(self):
        return 'common %d' % (self.id or 0)

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()

        super(CommonModel, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)


