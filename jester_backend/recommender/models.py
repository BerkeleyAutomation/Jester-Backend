from django.db import models
from django.utils import timezone


class User(models.Model):
    cluster_id = models.IntegerField('cluster id', default=-1)
    jokes_rated = models.IntegerField('jokes rated', default=0)

    def __unicode__(self):
        return '(id={0}, cluster_id={1}, jokes_rated={2})'.\
            format(self.id, self.cluster_id, self.jokes_rated)


class Joke(models.Model):
    joke_id = models.AutoField('joke id', primary_key=True)
    joke_text = models.CharField('joke text', max_length=2048)


class Rating(models.Model):
    user = models.ForeignKey(User)
    joke = models.ForeignKey(Joke)
    joke_idx = models.IntegerField('joke idx', default=-1)
    timestamp = models.DateTimeField('time stamp', default=timezone.now)

