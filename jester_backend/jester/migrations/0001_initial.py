# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Joke',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_params', models.TextField(default=b'', verbose_name=b'model params')),
                ('joke_text', models.TextField(verbose_name=b'joke text')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rater',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_params', models.TextField(default=b'', verbose_name=b'model parameters')),
                ('jokes_rated', models.IntegerField(default=0, verbose_name=b'jokes rated')),
                ('last_requested_joke_type', models.IntegerField(default=1)),
                ('stale', models.BooleanField(default=True, verbose_name=b'stale')),
                ('last_requested_joke', models.ForeignKey(default=None, to='jester.Joke', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating', models.DecimalField(verbose_name=b'rating', max_digits=6, decimal_places=4)),
                ('timestamp', models.DateTimeField(null=True, verbose_name=b'time stamp', blank=True)),
                ('rating_type', models.IntegerField(default=1)),
                ('joke', models.ForeignKey(to='jester.Joke')),
                ('user', models.ForeignKey(to='jester.Rater')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecommenderLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(null=True, verbose_name=b'time stamp', blank=True)),
                ('action', models.TextField(verbose_name=b'action')),
                ('user', models.ForeignKey(to='jester.Rater')),
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
            name='UserLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(verbose_name=b'time stamp')),
                ('ip_address', models.IPAddressField(null=True, verbose_name=b'ip address')),
                ('action', models.TextField(verbose_name=b'action')),
                ('action_type', models.IntegerField(default=0)),
                ('params', models.TextField(default=b'', null=True, verbose_name=b'params')),
                ('user', models.ForeignKey(to='jester.Rater')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
