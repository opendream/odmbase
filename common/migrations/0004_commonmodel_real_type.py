# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('common', '0003_auto_20150211_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='commonmodel',
            name='real_type',
            field=models.ForeignKey(default=4, editable=False, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
    ]
