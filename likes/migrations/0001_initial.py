# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0004_commonmodel_real_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('commonmodel_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='common.CommonModel')),
                ('dst', models.ForeignKey(related_name='likes', verbose_name='Destination', to='common.CommonModel')),
                ('src', models.ForeignKey(related_name='user_likes', verbose_name='Created by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('common.commonmodel',),
        ),
    ]
