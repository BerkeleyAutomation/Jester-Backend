"""
    A collection of useful utility functions. Contains the

    Note: Some of these functions assume that the required tables are empty,
    and that AUTO_INCREMENT begins from 1.

    In MySQL, tables can be emptied using:
        DELETE FROM <table name>;

    The AUTO_INCREMENT of a table can be reset to one using:
        ALTER TABLE <table name> AUTO_INCREMENT = 1;\
"""
from __future__ import division
import re
import django
import numpy as np
import os


__author__ = 'Viraj Mahesh'


# Setup code required before importing modules
os.environ['DJANGO_SETTINGS_MODULE'] = 'jester_backend.settings'
django.setup()

from jester.models import *

IMPORTED_JOKES = True
IMPORTED_OLD_RATINGS = True
IMPORTED_NEW_RATINGS = True
EXPORTED_RATINGS = False

# Gauge set jokes, indexed from 0 (according to the numpy dataset). To access
# the same joke in MySQL add 1 to these indices
GAUGE_SET = np.array([8, 61])
OFFSET = 73421


def import_jokes(clear_db=True):
    """
    Imports the jokes from the jokes.dat file into the MySQL database.

    Uses regex to extract joke text and indices from the data.

    Assumes that the table jester_joke in the database jester_db is empty,
    and that AUTO_INCREMENT for that table is 1. These conditions must be met
    in order for the jokes to be imported correctly

    :param clear_db: If True, then clears all previously imported jokes
    before importing. This does not reset AUTO_INCREMENT to 1
    :return: None
    """
    # Clear out table if necessary
    if IMPORTED_JOKES:
        return
    if clear_db:
        for joke in Joke.objects.all():
            joke.delete()
    # Read all the jokes into memory
    joke_file = open('../data/jokes.dat')
    joke_text = joke_file.read()
    # Remove all newline characters
    joke_text = joke_text.replace('\r', '')
    joke_text = joke_text.replace('\n', '')
    # Use regex to extract joke text and id, and use the information to
    # populate the db
    pattern = re.compile(r'(\d+):(<p>.+?</p>)')
    for match in pattern.finditer(joke_text):
        text = match.group(2)
        joke = Joke(joke_text=text)
        joke.save()
    # Close the file
    joke_file.close()


def get(Model, **kwargs):
    """
    Returns an list of objects of type Model that satisfy the conditions
    determined by **kwargs. If no such object exists then a new object is
    created with the properties specified by **kwargs

    :param Model: The class of the objects that must be found/created.
    :param kwargs: Variable number of keyword arguments used to filter/create objects
    :return: A list of objects that match the conditions
    """
    objects = Model.objects.filter(**kwargs)
    if not objects:
        objects = [Model(**kwargs)]
    return objects


def count_lines(file):
    """
    Counts the number of lines in a file by reading it line by line. Resets
    the file pointer to the beginning of the file

    :param file: The file to read from.
    :return: Then number of lines in the file.
    """
    line_count = 0
    for _ in file:
        line_count += 1
    file.seek(0)
    return line_count


def import_old_ratings():
    """
    Imports ratings from the jester 4 file which is in csv format. Creates new
    users in the jester_user table if necessary. Also updates the rating_count
    for each user.

    Assumes that no other ratings exist in the jester_rating table.

    Timestamps are NULL, as this information is missing. Joke_idxs are 0, as
    this information is missing.

    :return: None
    """
    if IMPORTED_OLD_RATINGS:
        return
    jester_4_ratings = file('../data/jester_4_ratings.csv')
    # Counting the number of lines in the file for progress report
    line_count = count_lines(jester_4_ratings)
    print 'Counted {0} lines'.format(line_count)
    # Read each rating line by line
    for idx, rating in enumerate(jester_4_ratings):
        # Progress Report every 1%
        if idx % (line_count // 100) == 0:
            print 'Completed {0}% of data import'.format(idx / line_count * 100)
        # Split the rating into individual components and parse
        user_id, joke_id, rating = rating.split(',')
        user_id, joke_id, rating = int(user_id), int(joke_id), float(rating)
        # Get or create objects corresponding to the parameters
        user = get(User, id=user_id)[0]
        joke = get(Joke, id=joke_id)[0]
        # Create a new rating to insert into the db. Note that timestamp
        # and joke idx (i.e order of joke presentation) is missing in this dataset
        rating = Rating(user=user, joke=joke, joke_rating_idx=0, rating=rating, timestamp=None)
        user.increment_rated_and_save()
        rating.save()  # Save the newly read rating into the db
    # Close the file
    jester_4_ratings.close()


def import_new_ratings():
    """
    Imports ratings from the jester 5 file which is is csv format. Creates new
    users in the jester_table if necessary. Also updates the rating_count
    for each user.

    Assumes that no other ratings exist in the jester_rating table.

    Timestamps are NULL, as this information is missing.

    :return: None
    """
    if IMPORTED_NEW_RATINGS:
        return
    offset = User.objects.count()
    print '{0} ratings already in db'.format(offset)
    jester_5_ratings = file('../data/jester_5_ratings.csv')
    # Counting the number of lines in the file for progress report
    line_count = count_lines(jester_5_ratings)
    print 'Counted {0} lines'.format(line_count)
    for idx, rating in enumerate(jester_5_ratings):
        # Progress Report every 1%
        if idx % (line_count // 100) == 0:
            print 'Completed {0}% of data import'.format(idx / line_count * 100)
        # Split the rating into individual components and parse
        user_id, joke_id, joke_rating_idx, rating = rating.split(',')
        user_id, joke_id, joke_rating_idx, rating = int(user_id), int(joke_id), \
                                                    int(joke_rating_idx), float(rating)
        user = get(User, id=user_id + offset)[0]
        joke = get(Joke, id=joke_id)[0]
        rating = Rating(user=user, joke=joke, joke_rating_idx=joke_rating_idx,
                        rating=rating, timestamp=None)
        user.increment_rated_and_save()
        rating.save()
    # Close the file
    jester_5_ratings.close()


def export_old_ratings_as_matrix(save_file='../data/ratings.npy'):
    """
    Exports all the old ratings as a matrix

    :return: None
    """
    if EXPORTED_RATINGS:
        return
    # Get total number of jokes and users
    jokes = Joke.objects.count()
    users = User.objects.latest('id').id
    # Create an empty matrix of size U x J, where U is the number of users and
    # J is the number of jokes
    rating_matrix = np.empty((users, jokes))
    rating_matrix[:] = np.nan
    # Get users that have rated each joke and update rating matrix
    for id in xrange(1, jokes + 1):
        print 'Completed {0}% of matrix construction'.format(id / jokes * 100)
        joke = get(Joke, id=id)[0]
        for rating in Rating.objects.filter(joke=joke):
            rating_matrix[rating.user.id - 1][id - 1] = rating.rating
    # Remove the rows that have no ratings
    rows_to_delete = []
    for idx, row in enumerate(np.copy(rating_matrix)):
        # If all entries in the row are np.nan
        if np.count_nonzero(~np.isnan(row)) == 0:
            rows_to_delete.append(idx)
    print 'Before deletion, dim(Ratings Matrix) = {0} x {1}'. \
        format(*rating_matrix.shape)
    rating_matrix = np.delete(rating_matrix, rows_to_delete, axis=0)
    print 'After deletion, dim(Ratings Matrix) = {0} x {1}'. \
        format(*rating_matrix.shape)
    # Save the ratings matrix to file
    np.save(save_file, rating_matrix)


def main():
    pass


if __name__ == '__main__':
    main()