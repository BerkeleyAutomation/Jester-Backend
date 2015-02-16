from eigentaste import StoredEigentasteModel, JOKE_CLUSTERS
from django.http import HttpResponse
from jester.models import *
from scripts import get


GAUGE_SET_SIZE = 2
GAUGE_SET = [8, 54]


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
    else:
        response = recommend_joke(user.id)
    return HttpResponse(json.dumps(response), content_type="application/json")


def recommend_joke(user_id):
    recommender_model = RecommenderModel.objects.all()[0]
    stored_model = StoredEigentasteModel(recommender_model.data)
    user = get(User, id=user_id)[0]
    user_model = user.load_model()
    id = stored_model.recommend_joke(user_model)
    joke = get(Joke, id=id + 1)[0]
    return {'joke_id': int(id + 1), 'joke_text': joke.joke_text}


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
    joke_idx = user.jokes_rated + 1
    rating = Rating(user=user, joke=joke, joke_rating_idx=joke_idx,
                    rating=rating, timestamp=timezone.now())
    user.increment_rated_and_save()
    rating.save()
    if user.jokes_rated == GAUGE_SET_SIZE:
        assign_to_cluster(user.id)
    elif user.jokes_rated > GAUGE_SET_SIZE:
        update_user_model(user.id, joke.id)
    return HttpResponse('OK')


def assign_to_cluster(user_id):
    """
    Assigns a user to a cluster.
    :param user:
    :return: None
    """
    # Load the recommender model from MySQL db and load it into a python class
    recommender_model = RecommenderModel.objects.all()[0]
    stored_model = StoredEigentasteModel(recommender_model.data)
    # Load the user ratings, ordered by joke id
    user = [rating.to_float() for rating in
            get(Rating, user_id=user_id).order_by('joke_id')]
    # Project the user using the principal components calculated from the training set
    user = stored_model.transform(user)
    cluster_id = stored_model.classify(user)
    moving_averages = stored_model.moving_averages(cluster_id)
    model = {'user cluster id': int(cluster_id),
             'moving averages': moving_averages,
             'jokes rated': [0] * JOKE_CLUSTERS}
    store_user_params(user_id, model)
    update_gauge_set_ratings(user_id)


def store_user_params(user_id, model):
    user = get(User, id=user_id)[0]
    user.store_model_and_save(model)


def update_user_model(user_id, joke_id):
    user = get(User, id=user_id)[0]
    joke = get(Joke, id=joke_id)[0]
    rating = get(Rating, user_id=user_id, joke=joke)[0]
    model = user.load_model()
    # Increment the number of jokes rated from the cluster that this gauge
    # set joke belongs to.
    model['jokes rated'][joke.cluster_id()] += 1
    # Remove the least recent rating and insert the latest rating
    model['moving averages'][joke.cluster_id()].pop()
    model['moving averages'][joke.cluster_id()].append(rating.to_float())
    user.store_model_and_save(model)


def update_gauge_set_ratings(user_id):
    # Iterate through all the jokes in the gauge set
    for joke_id in GAUGE_SET:
        update_user_model(user_id, joke_id)


def register_user(request, email, password):
    print email, password