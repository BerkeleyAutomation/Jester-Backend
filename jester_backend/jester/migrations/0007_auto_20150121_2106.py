# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0006_modelobject'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ModelObject',
            new_name='Cluster',
        ),
        migrations.RenameField(
            model_name='cluster',
            old_name='params',
            new_name='data',
        ),
    ]
