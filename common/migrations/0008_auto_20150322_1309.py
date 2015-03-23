# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_auto_20150322_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commonmodel',
            name='changed',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 22, 13, 9, 27, 581008, tzinfo=utc), verbose_name='Changed', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='commonmodel',
            name='common_created_by',
            field=models.ForeignKey(blank=True, to='common.CommonModel', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='commonmodel',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 22, 13, 9, 27, 580966, tzinfo=utc), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
    ]
