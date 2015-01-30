# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0007_auto_20150121_2106'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecommenderModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='data',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
