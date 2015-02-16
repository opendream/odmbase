# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20150212_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Published'), (-1, 'Request for Approval'), (0, 'Draft'), (-2, 'Deleted'), (-3, 'Cancelled'), (-5, 'Paying'), (2, 'Paid'), (3, 'Delivered'), (-4, 'Sold')]),
            preserve_default=True,
        ),
    ]
