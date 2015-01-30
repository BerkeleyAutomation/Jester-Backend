# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0011_joke_current'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joke',
            name='current',
            field=models.BooleanField(default=False, verbose_name=b'current'),
            preserve_default=True,
        ),
    ]
