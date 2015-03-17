# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import odmbase.account.models
import odmbase.common.storage


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20150217_0941'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='address',
        ),
        migrations.RemoveField(
            model_name='user',
            name='description',
        ),
        migrations.RemoveField(
            model_name='user',
            name='phone',
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(storage=odmbase.common.storage.OverwriteStorage(), upload_to=odmbase.account.models.get_upload_path, null=True, verbose_name='Avartar', blank=True),
            preserve_default=True,
        ),
    ]
