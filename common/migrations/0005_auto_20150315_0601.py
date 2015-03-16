# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_commonmodel_real_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='ordering',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='priority',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
