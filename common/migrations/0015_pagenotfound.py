# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0014_variable'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageNotFound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
