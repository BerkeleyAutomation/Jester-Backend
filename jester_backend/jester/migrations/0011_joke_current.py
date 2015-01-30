# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0010_joke_model_params'),
    ]

    operations = [
        migrations.AddField(
            model_name='joke',
            name='current',
            field=models.TextField(default=False, verbose_name=b'current'),
            preserve_default=True,
        ),
    ]
