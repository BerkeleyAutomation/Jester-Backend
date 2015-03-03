from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from ipware.ip import get_real_ip
from enum import Enum
import json


class Joke(models.Model):
    """
    :param id: Automatically created by django (hence not defined below).
    Uniquely identifies a joke. Automatically increments when a joke is added.

    :param joke_text: The text of the joke. Contains HTML tags to preserve
    formatting when joke text is rendered.

    :param in_gague_set: True if this joke is part of the gauge set.

    :param current: True if this joke will still be displayed.
    """
    model_params = models.TextField('model params', default='')
    joke_text = models.TextField('joke text')

    def __unicode__(self):
        """
        :return: A string representation of the joke
        """
        return '(id={0})'.format(self.id)

    def store_model_and_save(self, model):
        self.model_params = json.dumps(model)
        self.save()

    def cluster_id(self):
        model = json.loads(self.model_params)
        return model['cluster id']


class Rater(models.Model):
    """
    :param id: Automatically created by django (hence not defined below).
    Uniquely identifies a user. Automatically increments when a user is added.

    :param cluster_id: The index (0 indexed) of the cluster that the user belongs to.
    Is initially -1, when the user has not been assigned to any cluster.

    :param jokes_rated: The number of jokes rated by the user. This should
    match the result of the SQL query:
        SELECT COUNT(*) FROM jester_ratings WHERE user_id=<user id>;
    When a new user is created, this parameter is 0.

    :param last_requested_joke: The last joke that was requested by the user.
    """
    user = models.OneToOneField(User)
    model_params = models.TextField('model parameters', default='')
    jokes_rated = models.IntegerField('jokes rated', default=0)
    last_requested_joke = models.ForeignKey(Joke, default=None, blank=True, null=True)

    def increment_rated_and_save(self):
        """
        Increments the number of jokes rated by 1 and saves changes

        :return: None
        """
        self.jokes_rated += 1
        self.save()

    def store_model_and_save(self, model):
        self.model_params = json.dumps(model)
        self.save()

    def load_model(self):
        return json.loads(self.model_params)

    def __unicode__(self):
        """
        :return: A string representation of the user.
        """
        return '(id={0}, jokes_rated={1})'.\
            format(self.id, self.jokes_rated)


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

    :param timestamp: The time at which this rating was made.

    :param current: True if this rating is the latest rating submitted by the user.
    True by default, in order to ensure correctness for old data.
    """
    user = models.ForeignKey(Rater)
    joke = models.ForeignKey(Joke)
    joke_rating_idx = models.IntegerField('joke idx', default=-1)
    rating = models.DecimalField('rating', decimal_places=4, max_digits=6, default=99)
    timestamp = models.DateTimeField('time stamp', default=timezone.now, blank=True, null=True)

    def to_float(self):
        return float(self.rating)

    def __unicode__(self):
        """
        :return: A string representation of the rating
        """
        return '(user_id={0}, joke_id={1}, joke_idx={2}, rating={3}, timestamp={4})'.\
            format(self.user.id, self.joke.id,
                   self.joke_rating_idx, self.rating, self.timestamp)


class RecommenderModel(models.Model):
    """
    Stores JSON formatted python objects, that represent the recommender model.
    """
    data = models.TextField(default='')

    def store(self, model):
        self.data = json.dumps(model.export_model())


class Action(Enum):
    """
    Enum that represents different categories of user actions
    """
    rating = 0
    slider_position_change = 1
    logout = 2


class UserAction(models.Model):
    """
    Represents an action executed by the user

    :param: timestamp: Records the time the action took place.

    :param: ip_addr: The IP Address of the user. An IP address of wwww

    :param: action: A string representing the action taken by the user

    :param: action_type: An integer that represent which category the
    user action falls under.
    """
    timestamp = models.DateTimeField('time stamp', default=timezone.now,
                                     blank=True, null=True)
    ip_addr = models.IPAddressField('ip address', null=True)
    action = models.TextField('action')
    action_type = models.IntegerField('action type', default=-1)


    @staticmethod
    def log_submission(request, user_id, joke_id, rating):
        action = 'User {0} submitted rating of {1} for joke {2}'.\
            format(user_id, rating.to_float(), joke_id)
        user_action = \
            UserAction(timestamp=timezone.now(), ip_addr=get_real_ip(request),
                       action=action, action_type=Action.rating)
        user_action.save()


class RecommenderAction(models.Model):
    """
    Represents an action executed by the recommender system

    :param: timesetamp: Records the time the action took place/
    """
    timestamp = models.DateTimeField('time stamp',default=timezone.now,
                                     blank=True, null=True)
    action = models.TextField('action')