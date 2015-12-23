# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0016_auto_20150611_0233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commonmodel',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Published'), (-1, 'Request for Approval'), (0, 'Draft'), (-2, 'Deleted'), (-3, 'Cancelled'), (-5, 'Paying'), (2, 'Authorized'), (3, 'Delivered'), (6, 'Sold'), (-4, 'Old Sold'), (4, 'Settled'), (5, 'Completed')]),
            preserve_default=True,
        ),
    ]
