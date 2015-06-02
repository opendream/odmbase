# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0010_auto_20150325_0711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commonmodel',
            name='changed',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Changed'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='commonmodel',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created'),
            preserve_default=True,
        ),
    ]
