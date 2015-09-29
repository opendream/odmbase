# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0016_auto_20150611_0233'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('commonmodel_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='common.CommonModel')),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('dst', models.ForeignKey(related_name='user_message_dst', to=settings.AUTH_USER_MODEL)),
                ('src', models.ForeignKey(related_name='user_message_src', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('common.commonmodel',),
        ),
    ]
