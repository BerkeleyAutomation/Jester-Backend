from __future__ import division
import django
import numpy as np
from matplotlib import pyplot as plt
import os

__author__ = 'Viraj Mahesh'

# Setup code required before importing modules
os.environ['DJANGO_SETTINGS_MODULE'] = 'jester_backend.settings'
django.setup()

from jester.models import *


def display_user_stats(users):
    num_jokes_rated = [user.jokes_rated for user in users]
    print 'Total number of users: {0}'.format(len(users))
    print 'Mean # of jokes rated: {0}'.format(np.mean(num_jokes_rated))
    print 'Median # of jokes rated: {0}'.format(np.median(num_jokes_rated))
    print 'Max. number of jokes rated: {0}'.format(np.max(num_jokes_rated))
    print 'Min. number of jokes rated: {0}'.format(np.min(num_jokes_rated))
    display_num_jokes_rated_histogram(num_jokes_rated)


def display_num_jokes_rated_histogram(num_jokes_rated):
    plt.title('Histogram of number of ratings by user')
    plt.xlabel('Number of ratings')
    plt.ylabel('Number of users')
    plt.grid(True)
    plt.hist(num_jokes_rated)
    plt.show()


def display_ratings_stats(ratings):
    print 'Total number of ratings: {0}'.format(len(ratings))
    print 'Mean rating: {0}'.format(np.mean(ratings))
    print 'Median rating: {0}'.format(np.median(ratings))
    print 'Std. Deviation: {0}'.format(np.std(ratings))
    display_ratings_histogram(ratings)


def display_ratings_histogram(ratings):
    plt.title('Histogram of ratings')
    plt.xlabel('Rating')
    plt.ylabel('# of ratings')
    plt.grid(True)
    plt.hist(ratings, bins=20, range=(-10.0, 10.0))
    plt.show()


def main():
    ratings = [rating.to_float() for rating in Rating.objects.all()]
    users = [user for user in Rater.objects.all()]

    display_user_stats(users)
    display_ratings_stats(ratings)


if __name__ == '__main__':
    main()
