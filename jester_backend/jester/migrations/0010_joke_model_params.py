# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0009_auto_20150121_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='joke',
            name='model_params',
            field=models.TextField(default=b'', verbose_name=b'model params'),
            preserve_default=True,
        ),
    ]
