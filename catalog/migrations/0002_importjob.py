# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import paucore.data.fields
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('celery_id', models.CharField(max_length=255, null=True, blank=True)),
                ('created', paucore.data.fields.CreateDateTimeField(default=datetime.datetime.utcnow, blank=True)),
                ('updated', paucore.data.fields.LastModifiedDateTimeField(blank=True)),
                ('extra', paucore.data.fields.DictField(default=dict, editable=False)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Running'), (2, b'Done'), (3, b'Failed')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
