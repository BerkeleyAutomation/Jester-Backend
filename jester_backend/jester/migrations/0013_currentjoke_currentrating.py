# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jester', '0012_auto_20150128_0045'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentJoke',
            fields=[
                ('joke_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jester.Joke')),
            ],
            options={
            },
            bases=('jester.joke',),
        ),
        migrations.CreateModel(
            name='CurrentRating',
            fields=[
                ('rating_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='jester.Rating')),
            ],
            options={
            },
            bases=('jester.rating',),
        ),
    ]
