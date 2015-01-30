# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0005_auto_20150121_1720'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('params', models.TextField(verbose_name=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
