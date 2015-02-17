# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import odmbase.account.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to=odmbase.account.models.get_upload_path, blank=True),
            preserve_default=True,
        ),
    ]
