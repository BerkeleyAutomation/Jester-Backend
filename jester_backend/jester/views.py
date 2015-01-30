import json
import pickle

from jsonpickle import decode
from django.http import HttpResponse

from eigentaste.eigentaste import Point
from jester.models import *


GAUGE_SET_SIZE = 2
GAUGE_SET = [9, 62]


def delete_all_users():
    """
    Deletes all users from the database.
    ** FOR INTERNAL USE ONLY **
    """
    User.objects.clear()


def new_user(request):
    """
    Creates a new user and returns the user id. This should be the first
    API function called by Jester.
    """
    user = User()
    user.save()
    return HttpResponse(user.id)


def request_joke(request, user_id):
    """
    Returns the next joke for the specified user id.

    :return: A JSON formatted HTTP response, with the following fields:

    'joke_id': The id number of the joke. Uniquely identifies the joke.
    'joke_text': HTML formatted text that is used to display the joke.
    """
    # Select user with the corresponding id
    user = User.objects.filter(id=user_id)[0]
    response = {}  # No initial response
    # User has not finished rating gauge set jokes
    if user.jokes_rated < GAUGE_SET_SIZE:
        joke_id = GAUGE_SET[user.jokes_rated]  # Get joke id of gauge set
        required_joke = Joke.objects.filter(id=joke_id)[0]  # Load the joke from db
        # Format the joke id and text as a JSON response
        response = {'joke_id':joke_id, 'joke_text':required_joke.joke_text}
    # TODO: User has rated gauge set jokes and needs recommended jokes
    return HttpResponse(json.dumps(response), content_type="application/json")


def rate_joke(request, user_id, joke_id, rating):
    """
    Accepts a rating from the user and stores it. Updates user information
    as well. Verifies that user id and joke id are valid.

    :param user_id: Uniquely identifies the user.
    :param joke_id: Uniquely identifies the joke rated by the user.
    :param rating: The rating value, expressed as a number between -10 and 10.
    :return: An HTTP response confirming that the rating was successfully processed.
    """
    # Get the user and joke that corresponding to this rating
    user = User.objects.filter(id=user_id)[0]
    joke = Joke.objects.filter(id=joke_id)[0]
    rating = float(rating)
    # TODO: Validate user id and joke id.
    joke_idx = user.jokes_rated + 1
    rating = Rating(user=user, joke=joke, joke_rating_idx=joke_idx,
                    rating=rating, timestamp=timezone.now())
    user.increment_rated_and_save()
    rating.save()
    if user.jokes_rated == GAUGE_SET_SIZE:
        assign_to_cluster(user)
    return HttpResponse('OK')


def assign_to_cluster(user):
    """
    Assigns a user to a cluster.
    :param user:
    :return:
    """
    pca_model = pickle.loads(PCAModel.objects.all()[0].data)
    user_ratings = []
    for rating in Rating.objects.filter(user=user).order_by('id'):
        user_ratings.append(float(rating.rating))
    projected_rating = pca_model.transform(user_ratings)[0]
    projected_rating = Point(*projected_rating)
    clusters = Cluster.objects.all()
    print decode(clusters[0].data)


def register_user(request, email, password):
    print email, password