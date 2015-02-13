# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Joke',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('in_gauge_set', models.BooleanField(default=False, verbose_name=b'in gauge set')),
                ('model_params', models.TextField(default=b'', verbose_name=b'model params')),
                ('joke_text', models.TextField(verbose_name=b'joke text')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('joke_rating_idx', models.IntegerField(default=-1, verbose_name=b'joke idx')),
                ('rating', models.DecimalField(default=99, verbose_name=b'rating', max_digits=6, decimal_places=4)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name=b'time stamp', blank=True)),
                ('current', models.BooleanField(default=True, verbose_name=b'current')),
                ('joke', models.ForeignKey(to='jester.Joke')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
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
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_params', models.TextField(default=b'', verbose_name=b'model parameters')),
                ('jokes_rated', models.IntegerField(default=0, verbose_name=b'jokes rated')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(to='jester.User'),
            preserve_default=True,
        ),
    ]
