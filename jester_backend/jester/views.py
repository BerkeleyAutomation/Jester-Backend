from eigentaste import StoredEigentasteModel, JOKE_CLUSTERS
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from jester.models import *
from jester import *
from random import SystemRandom


GAUGE_SET_SIZE = 2
GAUGE_SET = [8, 54]
GAUGE_SET_JOKES = [Joke.objects.get(id=8), Joke.objects.get(id=54)]
PROB_RANDOM_JOKE = 0.3  # Probability of recommending a random joke

rng = SystemRandom()  # Random Number Generator


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
    user = get_user(request)
    stale, random, gauge = True, False, False

    if not user.stale:  # User did not submit rating for last joke
        joke = user.last_requested_joke
        stale = False
    elif user.jokes_rated < GAUGE_SET_SIZE:
        joke_id = GAUGE_SET[user.jokes_rated]  # Get joke id of gauge set.
        joke = Joke.objects.get(id=joke_id)  # Load the joke from db.
        gauge = True
    elif rng.random() < PROB_RANDOM_JOKE:  # Choose a random unrated joke
        user_model = user.load_model()
        unrated_jokes = Joke.objects.exclude(id__in=user_model['rated ids'])
        joke = rng.choice(unrated_jokes)
        random = True
    else:  # Use Eigentaste to select a joke
        joke = recommend_joke(user)

    if stale:  # User needs a new joke
        user.requested_new_joke(joke, random, gauge)
    log_request_joke(request, user, joke, stale, random, gauge)

    # Return the joke as a JSON object
    response = {'joke_id': joke.id, 'joke_text': joke.joke_text}
    return HttpResponse(json.dumps(response), content_type="application/json")


def recommend_joke(user):
    recommender_model = RecommenderModel.objects.get()
    stored_model = StoredEigentasteModel(recommender_model.data)
    joke = stored_model.recommend_joke(user)
    prediction = stored_model.get_prediction(user, joke)
    log_prediction(user, joke, prediction)
    return joke


def rate_joke(request, joke_id, rating):
    """
    Accepts a rating from the user and stores it. Updates user information
    as well. Verifies that user id and joke id are valid.

    :param joke_id: Uniquely identifies the joke rated by the user.
    :param rating: The rating value, expressed as a number between -10 and 10.
    :return: An HTTP response confirming that the rating was successfully processed.
    """
    user = get_user(request)
    joke = Joke.objects.get(id=joke_id)
    rating = Rating.create(user, joke, float(rating))

    user.increment_rated_and_save()
    rating.save()

    if user.jokes_rated == GAUGE_SET_SIZE:
        assign_to_cluster(user)
    elif user.jokes_rated > GAUGE_SET_SIZE:
        update_user_model(user, joke, rating)

    log_rating(request, user, joke, rating)
    return HttpResponse('OK')


def assign_to_cluster(user):
    """
    Assigns a user to a cluster.

    :param user_id: The user_id of the user.
    """
    # Load the recommender model from MySQL db and load it into a python class.
    recommender_model = RecommenderModel.objects.get()
    stored_model = StoredEigentasteModel(recommender_model.data)

    # Load the user ratings, ordered by joke id
    user_ratings = [rating.to_float() for rating
                    in Rating.objects.filter(user=user).order_by('joke')]
    # Project the user using the principal components calculated from the training set.
    user_ratings = stored_model.transform(user_ratings)
    cluster_id = stored_model.classify(user_ratings)

    # Initialize the moving averages vectors
    moving_averages = stored_model.moving_averages(cluster_id)
    model = {
        'user cluster id': int(cluster_id),
        'moving averages': moving_averages,
        'jokes rated': [0] * JOKE_CLUSTERS,
        'rated ids': []
    }
    # Store the user model information in the db. Update the user model with
    # the gauge set ratings.

    store_user_params(user, model)
    update_gauge_set_ratings(user)


def store_user_params(user, model):
    """
    Stores a user model in the db.

    :param user_id: The user whose model we want to update.
    :param model: The model we want to save.
    """
    user.store_model_and_save(model)


def update_user_model(user, joke, rating):
    """
    Loads a user model and updates it with the rating for a particular
    joke. Saves the updated user model in the db.

    """
    model = user.load_model()
    recommender_model = RecommenderModel.objects.get()
    stored_model = StoredEigentasteModel(recommender_model.data)
    prediction = stored_model.get_prediction(user, joke)

    model['jokes rated'][joke.cluster_id()] += 1
    model['moving averages'][joke.cluster_id()].pop(0)
    model['moving averages'][joke.cluster_id()].append(rating.to_float())
    model['rated ids'].append(joke.id)

    user.store_model_and_save(model)
    log_prediction(user, joke, prediction)


def update_gauge_set_ratings(user):
    for joke in GAUGE_SET_JOKES:
        rating = Rating.objects.get(user=user, joke=joke)
        update_user_model(user, joke, rating)


def log_slider(request, old_rating, new_rating):
    user = get_user(request)
    old_rating, new_rating = float(old_rating), float(new_rating)
    log_slider_movement(request, user, old_rating, new_rating)
    return HttpResponse("OK")


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
    log_logout(request, get_user(request))
    logout(request)
    return HttpResponse('OK')


def join_mailing_list(request):
    """
    Adds a user's email and reference source to the mailing list.

    """
    email, reference = request.GET.get('email'), request.GET.get('reference')
    MailingListMember.join_mailing_list(email, reference)
    return HttpResponse('OK')