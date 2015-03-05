from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from ipware.ip import get_real_ip
from django_enumfield import enum
import json


class Joke(models.Model):
    """
    Represents a joke in the Jester system.

    :param joke_text: The text of the joke. Contains HTML tags to preserve
        formatting when joke text is rendered.
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


class RatingType(enum.Enum):
    """
    Enum representing different types of ratings
    """
    GAUGE = 1
    RANDOM = 2
    RECOMMENDED = 3

    labels = {
        GAUGE: 'Gauge',
        RANDOM: 'Random',
        RECOMMENDED: 'Recommended'
    }


class Rater(models.Model):
    """
    Represents a User that has clicked the 'Begin' button and can submit ratings

    :param model_params: JSON formatted object with the following fields:
        {

        }
    :param jokes_rated: The number of jokes rated by the user.
    :param last_requested_joke: The last joke that was requested by the user.
    :param stale: Identifies whether the user has already rated the last
        requested joke.
    """
    user = models.OneToOneField(User)
    model_params = models.TextField('model parameters', default='')
    jokes_rated = models.IntegerField('jokes rated', default=0)
    last_requested_joke = models.ForeignKey(Joke, default=None, null=True)
    last_requested_joke_type = enum.EnumField(RatingType)
    stale = models.BooleanField('stale', default=True)

    def increment_rated_and_save(self):
        """
        Increments the number of jokes rated by 1 and saves changes
        """
        self.stale = True
        self.jokes_rated += 1
        self.save()

    def store_model_and_save(self, model):
        self.model_params = json.dumps(model)
        self.save()

    def load_model(self):
        return json.loads(self.model_params)

    def requested_new_joke(self, joke, random, gauge):
        if gauge:
            self.last_requested_joke_type = RatingType.GAUGE
        elif random:
            self.last_requested_joke_type = RatingType.RANDOM
        else:
            self.last_requested_joke_type = RatingType.RECOMMENDED

        self.last_requested_joke = joke
        self.stale = False
        self.save()

    def __unicode__(self):
        """
        :return: A string representation of the user.
        """
        return '(id={0}, jokes_rated={1})'.format(self.id, self.jokes_rated)


class Rating(models.Model):
    """
    Represents a rating submitted by the user

    :param user: Identifies the user that has submitted this rating. This user
        must exist in the jester_user table.
    :param joke: Identifies the joke for which this rating has been submitted. This
        joke must exist in the jester_joke table.
    :param joke_rating_idx: The index of this joke in the sequence of presented jokes.
        If the information is missing, this field will be 0.
    :param rating: The rating of the specified joke by the user, which is a
        decimal value from -10 to 10.
    :param timestamp: The time at which this rating was made.
    :param rating_type: Distinguishes between random, recommended and gauge set ratings
    """
    user = models.ForeignKey(Rater)
    joke = models.ForeignKey(Joke)
    rating = models.DecimalField('rating', decimal_places=4, max_digits=6)
    timestamp = models.DateTimeField('time stamp', blank=True, null=True)
    rating_type = enum.EnumField(RatingType)

    def to_float(self):
        return float(self.rating)

    @staticmethod
    def create(user, joke, rating):
        return Rating(user=user,
                      joke=joke,
                      rating=rating,
                      timestamp=timezone.now(),
                      rating_type=user.last_requested_joke_type)

    def __unicode__(self):
        """
        :return: A string representation of the rating
        """
        return '(user_id={0}, joke_id={1}, joke_idx={2}, rating={3}, timestamp={4})'.\
            format(self.user.id, self.joke.id,
                   self.joke_rating_idx, self.rating, self.timestamp)


class RecommenderModel(models.Model):
    """
    Stores a JSON formatted python object, that represent the recommender model.
    """
    data = models.TextField(default='')

    def store(self, model):
        self.data = json.dumps(model.export_model())


class UserActionType(enum.Enum):
    """
    Enum that represents different categories of user actions
    """
    RATING = 0
    SLIDER = 1
    LOGOUT = 2
    REQUEST_JOKE = 3

    labels = {
        RATING: 'Rating',
        SLIDER: 'Slider Moved',
        LOGOUT: 'Logout',
        REQUEST_JOKE: 'Request Joke'
    }


class UserLog(models.Model):
    """
    Represents an action executed by the user

    :param: timestamp: Records the time the action took place.
    :param: ip_address: The IP Address of the user. An IP address of wwww
    :param: action: A string representing the action taken by the user
    :param: action_type: An integer that represent which category the
        user action falls under.
    :param: The user that performed the action
    """
    timestamp = models.DateTimeField('time stamp')
    ip_address = models.IPAddressField('ip address', null=True)
    action = models.TextField('action')
    action_type = enum.EnumField(UserActionType)
    user = models.ForeignKey(Rater)
    params = models.TextField('params', default='', null=True)

    @staticmethod
    def log_rating(request, user, joke, rating):
        action = ('User {0} submitted rating of {1} for joke {2}'.
                  format(user.id, rating.to_float(), joke.id))
        user_action = UserLog(timestamp=timezone.now(),
                              ip_address=get_real_ip(request),
                              action=action,
                              action_type=UserActionType.RATING,
                              user=user)
        user_action.save()

    @staticmethod
    def log_logout(request):
        user = request.user.rater
        action = 'User {0} logged out'.format(user.id)
        user_action = UserLog(timestamp=timezone.now(),
                              ip_address=get_real_ip(request),
                              action=action,
                              action_type=UserActionType.LOGOUT,
                              user=user)
        user_action.save()

    @staticmethod
    def log_request_joke(request, user, joke, stale, random, gauge):
        if not stale:
            method = 'requested but not rated'
        elif gauge:
            method = 'part of gauge set'
        elif random:
            method = 'randomly chosen'
        else:
            method = 'recommended'
        action = ('User {0} requested joke and server responded with joke {1}'
                 ' which was {2}'.format(user.id, joke.id, method))
        user_action = UserLog(timestamp=timezone.now(),
                              ip_address=get_real_ip(request),
                              action=action,
                              action_type=UserActionType.REQUEST_JOKE,
                              user=user)
        user_action.save()


class RecommenderActionType(enum.Enum):
    pass


class RecommenderLog(models.Model):
    """
    Represents an action executed by the recommender system.

    :param: timestamp: Records the time the action took place.
    """
    timestamp = models.DateTimeField('time stamp', blank=True, null=True)
    action = models.TextField('action')
    user = models.ForeignKey(Rater)

    @staticmethod
    def log_cluster_choice(user, item_cluster_idx, average):
        action = ('Selected cluster {0} with average {1} for User {2}'.
                  format(item_cluster_idx, average, user.id))
        recommender_action = RecommenderLog(timestamp=timezone.now(),
                                            action=action,
                                            user=user)
        recommender_action.save()

    @staticmethod
    def log_averages(user, averages):
        averages = ['{:0.2f}'.format(mean) for _, mean in averages]
        action = 'Averages: {0}'.format(averages)
        recommender_action = RecommenderLog(timestamp=timezone.now(),
                                            action=action,
                                            user=user)
        recommender_action.save()

    @staticmethod
    def log_prediction(user, joke, prediction):
        action = ('Predicted a rating of {0:.2f} for User {1} for Joke {2}'.
                  format(prediction, user.id, joke.id))
        recommender_action = RecommenderLog(timestamp=timezone.now(),
                                            action=action,
                                            user=user)
        recommender_action.save()