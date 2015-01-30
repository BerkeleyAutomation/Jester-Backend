# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0004_auto_20150120_2117'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='cluster_id',
        ),
        migrations.AddField(
            model_name='user',
            name='model_params',
            field=models.TextField(default=b'', verbose_name=b'model parameters'),
            preserve_default=True,
        ),
    ]
