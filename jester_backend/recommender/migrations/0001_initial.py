# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


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
            name='Ratings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('joke_idx', models.IntegerField(verbose_name=b'joke idx')),
                ('joke', models.ForeignKey(to='recommender.Joke')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(serialize=False, verbose_name=b'user id', primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ratings',
            name='user',
            field=models.ForeignKey(to='recommender.User'),
            preserve_default=True,
        ),
    ]
