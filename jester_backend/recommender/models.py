from django.db import models
from django.utils import timezone


class User(models.Model):
    user_id = models.AutoField('user id', primary_key=True)


class Joke(models.Model):
    joke_id = models.AutoField('joke id', primary_key=True)
    joke_text = models.CharField('joke text', max_length=2048)


class Rating(models.Model):
    user = models.ForeignKey(User)
    joke = models.ForeignKey(Joke)
    joke_idx = models.IntegerField('joke idx')
    timestamp = models.DateTimeField('time stamp', default=timezone.now)

