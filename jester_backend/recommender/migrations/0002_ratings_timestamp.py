# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ratings',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name=b'time stamp'),
            preserve_default=True,
        ),
    ]
