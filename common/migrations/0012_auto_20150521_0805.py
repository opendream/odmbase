# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0011_auto_20150501_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commonmodel',
            name='changed',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Changed', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='commonmodel',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
    ]
