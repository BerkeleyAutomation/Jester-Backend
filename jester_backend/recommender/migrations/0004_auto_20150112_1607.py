# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0003_auto_20150112_1603'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('joke_idx', models.IntegerField(verbose_name=b'joke idx')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'time stamp')),
                ('joke', models.ForeignKey(to='recommender.Joke')),
                ('user', models.ForeignKey(to='recommender.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='ratings',
            name='joke',
        ),
        migrations.RemoveField(
            model_name='ratings',
            name='user',
        ),
        migrations.DeleteModel(
            name='Ratings',
        ),
    ]
