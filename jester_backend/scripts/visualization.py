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


def freedman_diaconis(v):
    def IQR(v):
        return np.percentile(v, 75) - np.percentile(v, 25)
    h = 2 * IQR(v) * (len(v)) ** (-1/3)
    return int((np.max(v) - np.min(v))/h), h


def text_only_legend(s):
    blank_rectangle = plt.Rectangle((0, 0), 0, 0, alpha=0.0)
    plt.legend([blank_rectangle], [s], handlelength=0)


def display_user_stats(users):
    num_jokes_rated = [user.jokes_rated for user in users]
    print 'Total number of users: {0}'.format(len(users))
    print 'Mean # of jokes rated: {0}'.format(np.mean(num_jokes_rated))
    print 'Median # of jokes rated: {0}'.format(np.median(num_jokes_rated))
    print 'Max. number of jokes rated: {0}'.format(np.max(num_jokes_rated))
    print 'Min. number of jokes rated: {0}'.format(np.min(num_jokes_rated))
    display_num_jokes_rated_histogram(num_jokes_rated)


def display_num_jokes_rated_histogram(num_jokes_rated):
    bins, width = freedman_diaconis(num_jokes_rated)
    plt.title('Histogram of number of ratings by user')
    plt.xlabel('Number of ratings')
    plt.ylabel('Number of users')
    plt.grid(True)
    text_only_legend('bins={0}, width={1:.3f}'.format(bins, width))
    plt.hist(num_jokes_rated, bins=bins)
    plt.show()


def display_ratings_stats(ratings):
    print 'Total number of ratings: {0}'.format(len(ratings))
    print 'Mean rating: {0}'.format(np.mean(ratings))
    print 'Median rating: {0}'.format(np.median(ratings))
    print 'Std. Deviation: {0}'.format(np.std(ratings))
    display_ratings_histogram(ratings)


def display_ratings_histogram(ratings):
    bins, width = freedman_diaconis(ratings)
    plt.title('Histogram of ratings')
    plt.xlabel('Rating')
    plt.ylabel('# of ratings')
    plt.grid(True)
    text_only_legend('bins={0}, width={1:.3f}'.format(bins, width))
    plt.hist(ratings, bins=bins)
    plt.show()


def main():
    ratings = [rating.to_float() for rating in Rating.objects.all()]
    users = [user for user in Rater.objects.all()]

    display_user_stats(users)
    display_ratings_stats(ratings)


if __name__ == '__main__':
    main()
