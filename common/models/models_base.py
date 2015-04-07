# -*- coding: utf-8 -*-

import copy
from uuid import uuid1
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
import bleach

import re
from odmbase.common.constants import STATUS_CHOICES, STATUS_PUBLISHED


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

    CACHE_SEO_META = None

    class Meta:
        abstract = True

    def save(self, commit=True, force_insert=False, force_update=False, *args, **kwargs):

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

    def seo_meta(self):

        if self.CACHE_SEO_META:
            return self.CACHE_SEO_META

        # title ------------------------------------------
        title = self.unicode_string()

        # description ------------------------------------
        description = ''
        description_field = hasattr(self, 'SEO') and self.SEO.get('description')
        if description_field:
            if type(description_field) is list:
                description = ['%s\n%s' % (description, getattr(self, field)) for field in description_field]
            else:
                description = getattr(self, description_field)

        elif hasattr(self, 'description'):
            description = self.description

        # image ------------------------------------------
        image = ''
        image_field = hasattr(self, 'SEO') and self.SEO.get('image')
        if image_field:
            image = getattr(self, image_field)
            try:
                image = image.all()[0].image
            except:
                pass

        elif hasattr(self, 'image'):
            image = self.image
        elif hasattr(self, 'image_set'):
            try:
                image = self.image_set.all()[0].image
            except:
                pass

        image = image and image.url

        self.CACHE_SEO_META = {
            'title': strip_tags(title),
            'description': strip_tags(description),
            'image': image
        }
        return self.CACHE_SEO_META



class AbstractCommonTrashModel(AbstractCommonModel):
    is_deleted = models.BooleanField(default=False)
    objects = CommonTrashManager()

    class Meta:
        abstract = True

    def save(self, commit=True, force_insert=False, force_update=False, *args, **kwargs):
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

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(AbstractCachedModel, self).__init__(*args, **kwargs)
        self.var_cache = {}
        for var in self.cached_vars:
            try:
                self.var_cache[var] = copy.copy(getattr(self, var))
            except:
                self.var_cache[var] = None


class AbstractPermalink(models.Model):

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

    def save(self, commit=True, force_insert=False, force_update=False, *args, **kwargs):
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

    DEFAULT_STATUS = STATUS_PUBLISHED

    real_type = models.ForeignKey(ContentType, editable=False)

    common_created_by = models.ForeignKey('self', null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PUBLISHED)

    created = models.DateTimeField(_('Created'), auto_now_add=True, default=timezone.now)
    changed = models.DateTimeField(_('Changed'), auto_now=True, default=timezone.now)

    def __init__(self, *args, **kwargs):
        super(CommonModel, self).__init__(*args, **kwargs)

        if hasattr(self, 'DEFAULT_STATUS'):
            self._meta.get_field('status').default = self.DEFAULT_STATUS

    def __unicode__(self):
        return 'common %d' % (self.id or 0)

    def save(self, commit=True, force_insert=False, force_update=False, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()

        if hasattr(self, 'created_by'):
            self.common_created_by = self.created_by
        elif hasattr(self, 'CREATED_BY_FIELD'):
            self.common_created_by = getattr(self, self.CREATED_BY_FIELD)

        super(CommonModel, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)
