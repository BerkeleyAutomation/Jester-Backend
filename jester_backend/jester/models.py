from django.db import models
from django.utils import timezone


class User(models.Model):
    """
    :param id: Automatically created by django (hence not defined below).
    Uniquely identifies a user. Automatically increments when a user is added.
    :param cluster_id: The index (0 indexed) of the cluster that the user belongs to.
    Is initially -1, when the user has not been assigned to any cluster.
    :param jokes_rated: The number of jokes rated by the user. This should
    match the result of the SQL query:
        SELECT COUNT(*) FROM jester_ratings WHERE user_id=<user id>;
    When a new user is created, this parameter is 0.
    """
    model_params = models.TextField('model parameters', default='')
    jokes_rated = models.IntegerField('jokes rated', default=0)

    def __unicode__(self):
        """
        :return: A string representation of the user.
        """
        return '(id={0}, cluster_id={1}, jokes_rated={2})'.\
            format(self.id, self.cluster_id, self.jokes_rated)

    def increment_rated_and_save(self):
        """
        Increments the number of jokes rated by 1 and saves changes
        :return: None
        """
        self.jokes_rated += 1
        self.save()


class Joke(models.Model):
    """
    :param id: Automatically created by django (hence not defined below).
    Uniquely identifies a joke. Automatically increments when a joke is added.
    :param joke_text The text of the joke. Contains HTML tags to preserve
    formatting when joke text is rendered.
    :param in_gagueg_set True if this joke is part of the gauge set.
    """
    joke_text = models.TextField('joke text')
    in_gauge_set = models.BooleanField('in gauge set', default=False)

    def __unicode__(self):
        """
        :return: A string representation of the joke
        """
        return '(id={0})'.format(self.id)


class Rating(models.Model):
    """
    :param id: Automatically created by django (hence not defined below). Uniquely
    identifies a rating. Automatically increments when a rating is added.
    :param user: Identifies the user that has submitted this rating. This user
    must exist in the jester_user table.
    :param joke: Identifies the joke for which this rating has been submitted. This
    joke must exist in the jester_joke table.
    :param joke_idx: The index of this joke in the sequence of presented jokes.
    If the information is missing, this field will be 0.
    :param rating: The rating of the specified joke by the user, which is a
    decimal value from -10 to 10.
    :param timestamp: The time at which this rating was made. If the
    information is missing, this field will be NULL.
    :param current: True if this rating is the latest rating submitted by the user.
    True by default, in order to ensure correctness for old data.
    """
    user = models.ForeignKey(User)
    joke = models.ForeignKey(Joke)
    joke_rating_idx = models.IntegerField('joke idx', default=-1)
    rating = models.DecimalField('rating', decimal_places=4, max_digits=6, default=99)
    timestamp = models.DateTimeField('time stamp', default=timezone.now, blank=True, null=True)
    current = models.BooleanField('current', default=True)

    def __unicode__(self):
        """
        :return: A string representation of the rating
        """
        return '(user_id={0}, joke_id={1}, joke_idx={2}, rating={3}, timestamp={4})'.\
            format(self.user.id, self.joke.id,
                   self.joke_rating_idx, self.rating, self.timestamp)


class Objects(models.Model):
    """
    Stores objects for the learning model. Users refer to these objects.
    """
    params = models.TextField('')

