# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0002_auto_20150114_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='joke',
            name='in_gauge_set',
            field=models.BooleanField(default=False, verbose_name=b'in gauge set'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rating',
            name='current',
            field=models.BooleanField(default=True, verbose_name=b'current'),
            preserve_default=True,
        ),
    ]
