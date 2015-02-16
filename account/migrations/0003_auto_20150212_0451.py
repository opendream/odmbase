# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.db import models, migrations
import django.core.validators

import odmbase.account.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='address',
            field=models.TextField(null=True, verbose_name='Address', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='description',
            field=models.TextField(null=True, verbose_name='About you', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(unique=True, max_length=255, verbose_name='Email address'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=255, null=True, verbose_name='First name', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(upload_to=odmbase.account.models.get_upload_path, null=True, verbose_name='Avartar', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=255, null=True, verbose_name='Last name', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=255, null=True, verbose_name='Phone', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Required 30 characters or fewer. Letters, numbers and @/./+/-/_ characters', unique=True, max_length=30, verbose_name='Username', validators=[django.core.validators.RegexValidator(re.compile(b'^[\\w.@+-]+$'), 'Enter a valid username.', b'invalid')]),
            preserve_default=True,
        ),
    ]
