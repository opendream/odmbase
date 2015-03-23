# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_auto_20150322_1309'),
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
        migrations.AlterField(
            model_name='commonmodel',
            name='status',
            field=models.IntegerField(default=2, choices=[(1, 'Published'), (-1, 'Request for Approval'), (0, 'Draft'), (-2, 'Deleted'), (-3, 'Cancelled'), (-5, 'Paying'), (2, 'Paid'), (3, 'Delivered'), (-4, 'Sold'), (4, 'Settled')]),
            preserve_default=True,
        ),
    ]
