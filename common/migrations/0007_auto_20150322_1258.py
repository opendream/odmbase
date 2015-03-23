# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_auto_20150316_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='commonmodel',
            name='changed',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 22, 12, 58, 33, 430897, tzinfo=utc), verbose_name='Changed', auto_now=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commonmodel',
            name='common_created_by',
            field=models.ForeignKey(to='common.CommonModel', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commonmodel',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 22, 12, 58, 33, 430856, tzinfo=utc), verbose_name='Created', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commonmodel',
            name='status',
            field=models.IntegerField(default=-1, choices=[(1, 'Published'), (-1, 'Request for Approval'), (0, 'Draft'), (-2, 'Deleted'), (-3, 'Cancelled'), (-5, 'Paying'), (2, 'Paid'), (3, 'Delivered'), (-4, 'Sold'), (4, 'Settled')]),
            preserve_default=True,
        ),
    ]
