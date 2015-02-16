# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import odmbase.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(upload_to=odmbase.common.models.get_upload_path),
            preserve_default=True,
        ),
    ]
