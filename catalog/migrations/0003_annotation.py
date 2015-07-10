# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import paucore.data.fields
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_importjob'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quote', models.TextField()),
                ('text', models.TextField()),
                ('created', paucore.data.fields.CreateDateTimeField(default=datetime.datetime.utcnow, blank=True)),
                ('updated', paucore.data.fields.LastModifiedDateTimeField(blank=True)),
                ('article', models.ForeignKey(to='catalog.Article')),
                ('extra', paucore.data.fields.DictField(default=dict, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
