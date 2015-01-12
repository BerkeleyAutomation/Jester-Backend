import json
from django.http import HttpResponse
from recommender.models import User

GAUGE_SET_SIZE = 2

def delete_all_users():
    """
        Deletes all users from the database
    """
    User.objects.clear()


def new_user(request):
    """
        Creates a new user and returns the user id
    """
    user = User()
    user.save()
    return HttpResponse(user.id)


def request_joke(request, user_id):
    # Select the user with the corresponding id
    user = User.objects.filter(user_id=user_id)[0]
    if user.jokes_rated < GAUGE_SET_SIZE:
        pass  # Return gauge set joke
    # Return next prediction