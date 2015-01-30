# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0008_auto_20150121_2333'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecommenderModel',
            new_name='PCAModel',
        ),
    ]
