# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0002_ratings_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratings',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'time stamp'),
            preserve_default=True,
        ),
    ]
