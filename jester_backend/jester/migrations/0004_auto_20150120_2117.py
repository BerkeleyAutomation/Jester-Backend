# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0003_auto_20150120_2112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joke',
            name='joke_text',
            field=models.TextField(verbose_name=b'joke text'),
            preserve_default=True,
        ),
    ]
