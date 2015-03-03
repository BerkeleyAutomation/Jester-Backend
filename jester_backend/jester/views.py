from eigentaste import StoredEigentasteModel, JOKE_CLUSTERS
from django.contrib.auth import authenticate, login, logout
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


def get_user(request):
    """
    Obtains the user making the request. If this user is new to the Jester system
    then this function creates a new entry in the auth_users tables. If the user
    has pre-existing credentials, then this function authenticates the user.

    :return: A 'Rater' object that represents the user making the request.
    """
    if not request.user.is_authenticated():
        username = password = str(User.objects.count() + 1)
        User.objects.create_user(username, password=password)
        user = authenticate(username=username, password=password)
        user.is_active = True
        user.rater = Rater.objects.create(user=user)
        login(request, user)
    else:
        user = request.user
    return user.rater


def request_joke(request):
    """
    Returns the next joke for the specified user id.

    :return: A JSON formatted HTTP response, with the following fields:
        {
            'joke_id': The id number of the joke. Uniquely identifies the joke.
            'joke_text': HTML formatted text that is used to display the joke.
        }
    """
    user = get_user(request)  # Select user with the corresponding id.
    # User has not finished rating gauge set jokes.
    if user.jokes_rated < GAUGE_SET_SIZE:
        joke_id = GAUGE_SET[user.jokes_rated]  # Get joke id of gauge set.
        required_joke = Joke.objects.filter(id=joke_id)[0]  # Load the joke from db.
        # Format the joke id and text as a JSON response.
        user.last_requested_joke = required_joke
        response = {'joke_id': joke_id, 'joke_text': required_joke.joke_text}
    else:
        response = recommend_joke(user.id)
    return HttpResponse(json.dumps(response), content_type="application/json")


def recommend_joke(user_id):
    # Retrieve recommender model from the database.
    recommender_model = RecommenderModel.objects.all()[0]
    # Parse the JSON string into a python object.
    stored_model = StoredEigentasteModel(recommender_model.data)
    # Load the user and the user model information from the database.
    user = get(Rater, id=user_id)[0]
    user_model = user.load_model()
    # Get the id of next recommended joke from the recommender model.
    joke_id = stored_model.recommend_joke(user_model) + 1
    joke = get(Joke, id=joke_id)[0]
    return {'joke_id': int(joke_id), 'joke_text': joke.joke_text}


def rate_joke(request, joke_id, rating):
    """
    Accepts a rating from the user and stores it. Updates user information
    as well. Verifies that user id and joke id are valid.

    :param user_id: Uniquely identifies the user.
    :param joke_id: Uniquely identifies the joke rated by the user.
    :param rating: The rating value, expressed as a number between -10 and 10.
    :return: An HTTP response confirming that the rating was successfully processed.
    """
    # Get the user and joke that corresponding to this rating.
    user = get_user(request)
    joke = Joke.objects.filter(id=joke_id)[0]
    rating = float(rating)
    joke_idx = user.jokes_rated + 1
    rating = Rating(user=user, joke=joke, joke_rating_idx=joke_idx,
                    rating=rating, timestamp=timezone.now())
    user.increment_rated_and_save()
    rating.save()
    # Log this rating to the UserAction table
    UserAction.log_submission(request, user.id, joke.id, rating)
    # If the user has rated both jokes in the gauge set, assign to a cluster.
    if user.jokes_rated == GAUGE_SET_SIZE:
        assign_to_cluster(user.id)
    elif user.jokes_rated > GAUGE_SET_SIZE:
        update_user_model(user.id, joke.id)
    return HttpResponse('OK')


def assign_to_cluster(user_id):
    """
    Assigns a user to a cluster.

    :param user_id: The user_id of the user.
    """
    # Load the recommender model from MySQL db and load it into a python class.
    recommender_model = RecommenderModel.objects.all()[0]
    stored_model = StoredEigentasteModel(recommender_model.data)
    # Load the user ratings, ordered by joke id
    user = [rating.to_float() for rating in
            get(Rating, user_id=user_id).order_by('joke_id')]
    # Project the user using the principal components calculated from the training set.
    user = stored_model.transform(user)
    cluster_id = stored_model.classify(user)
    # Initialize the moving averages vectors
    moving_averages = stored_model.moving_averages(cluster_id)
    model = {'user cluster id': int(cluster_id),
             'moving averages': moving_averages,
             'jokes rated': [0] * JOKE_CLUSTERS}
    # Store the user model information in the db. Update the user model with
    # the gauge set ratings.
    store_user_params(user_id, model)
    update_gauge_set_ratings(user_id)


def store_user_params(user_id, model):
    """
    Stores a user model in the db.

    :param user_id: The user whose model we want to update.
    :param model: The model we want to save.
    """
    user = get(Rater, id=user_id)[0]
    user.store_model_and_save(model)


def update_user_model(user_id, joke_id):
    """
    Loads a user model and updates it with the rating for a particular
    joke. Saves the updated user model in the db.

    :param user_id: The user id of the user whose model we are updating
    :param joke_id: The joke id of the joke rated by the user.
    """
    user = get(Rater, id=user_id)[0]
    joke = get(Joke, id=joke_id)[0]
    rating = get(Rating, user_id=user_id, joke=joke)[0]
    model = user.load_model()
    # Increment the number of jokes rated from the cluster that this gauge
    # set joke belongs to.
    model['jokes rated'][joke.cluster_id()] += 1
    # Remove the least recent rating and insert the latest rating
    model['moving averages'][joke.cluster_id()].pop(0)
    model['moving averages'][joke.cluster_id()].append(rating.to_float())
    user.store_model_and_save(model)


def update_gauge_set_ratings(user_id):
    # Iterate through all the jokes in the gauge set
    for joke_id in GAUGE_SET:
        update_user_model(user_id, joke_id)


def register_user(request):
    """
    Registers a user's email address and their response to the
    'Where did you hear about Jester?' question.
    """
    email = request.GET.get('email')
    request.user.email = email
    request.user.save()


def logout_user(request):
    """
    Logs a user out and clears all session information.

    :param request: The HTTP request made while requesting a log out
    :return: An HTTP response confirming that the logout was successful
    """
    logout(request)
    return HttpResponse('OK')
