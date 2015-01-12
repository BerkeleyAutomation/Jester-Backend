# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Joke',
            fields=[
                ('joke_id', models.AutoField(serialize=False, verbose_name=b'joke id', primary_key=True)),
                ('joke_text', models.CharField(max_length=2048, verbose_name=b'joke text')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('joke_idx', models.IntegerField(default=-1, verbose_name=b'joke idx')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'time stamp')),
                ('joke', models.ForeignKey(to='recommender.Joke')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cluster_id', models.IntegerField(default=-1, verbose_name=b'cluster id')),
                ('jokes_rated', models.IntegerField(default=0, verbose_name=b'jokes rated')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(to='recommender.User'),
            preserve_default=True,
        ),
    ]
