# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_auto_20150315_0601'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ['ordering']},
        ),
    ]
