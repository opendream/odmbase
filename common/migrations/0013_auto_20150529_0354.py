# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0012_auto_20150521_0805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='ordering',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='image',
            name='priority',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
