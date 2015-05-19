from __future__ import division
from django.http import HttpResponse
from jester.models import *
from distutils.util import strtobool
from datetime import datetime, timedelta
from collections import OrderedDict
import numpy as np


__author__ = 'Viraj Mahesh'


def freedman_diaconis(v):
    """Uses the Freedman-Diaconis rule to calculate number of bins and bin width"""

    def IQR(v):
        return np.percentile(v, 75) - np.percentile(v, 25)

    h = (2 * IQR(v) * (len(v)) ** (-1 / 3))
    range = np.max(v) - np.min(v)
    bins = int(range / h)
    return bins, range / bins


def rating_histogram(request):
    start_date = datetime.strptime(request.GET.get('start_date'), '%m/%d/%Y')
    end_date = datetime.strptime(request.GET.get('end_date'), '%m/%d/%Y')
    filter_null = strtobool(request.GET.get('filter_null'))
    ratings = map(Rating.to_float,
                  Rating.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date))

    if filter_null:
        ratings = filter(lambda x: x != 0, ratings)
    bins, width = 20, 1  # Hardcoded number of bins. Works better
    hist, bin_edges = np.histogram(ratings, bins=bins)
    hist, bin_edges = hist.tolist(), bin_edges.tolist()

    response = {
        'heights': zip(np.add(bin_edges, width / 2), hist),
        'yAxis': {
            'min': 0,
            'max': np.max(hist)
        },
        'xAxis': {
            'min': -10.0,
            'max': 10.0,
            'tickPositions': bin_edges
        },
        'stats': {
            'bins': bins,
            'bin_width': width,
            'num_ratings': len(ratings),
            'mean_rating': np.mean(ratings),
            'median_rating': np.median(ratings)
        }
    }
    return HttpResponse(json.dumps(response), content_type='application/json')


def num_ratings_histogram(request):
    filter_null = strtobool(request.GET.get('filter_null'))
    num_ratings = map(Rater.num_jokes_rated, Rater.objects.all())

    if filter_null:
        num_ratings = filter(lambda x: x != 0, num_ratings)
    bins, width = freedman_diaconis(num_ratings)
    hist, bin_edges = np.histogram(num_ratings, bins=bins)
    hist, bin_edges = hist.tolist(), bin_edges.tolist()

    response = {
        'heights': zip(np.add(bin_edges, width / 2), hist),
        'yAxis': {
            'min': 0,
            'max': np.max(hist)
        },
        'xAxis': {
            'min': np.min(bin_edges),
            'max': np.max(bin_edges),
            'tickPositions': np.arange(bin_edges[0], width*bins, width*bins/10).tolist()
        },
        'stats': {
            'bins': bins,
            'bin_width': width,
            'num_ratings': len(num_ratings),
            'mean_num_ratings': np.mean(num_ratings),
            'median_rating': np.median(num_ratings)
        }
    }
    return HttpResponse(json.dumps(response), content_type='application/json')


def num_ratings_over_time(request):
    delta = timedelta(days=1)
    now = datetime(day=1, month=4, year=2015).date()
    end = datetime.now().date()

    counts = OrderedDict()

    while now <= end:
        counts[now] = 0
        now += delta

    for rating in Rating.objects.all():
        counts[rating.date()] += 1

    dates, ratings = counts.keys(), counts.values()
    dates = map(lambda x: x.strftime('%d-%b-%y'), dates)

    response = {
        'heights': ratings,
        'xAxis': {
            'categories': dates
        },
        'yAxis': {
            'min': np.min(ratings),
            'max': np.max(ratings)
        }
    }
    return HttpResponse(json.dumps(response), content_type='application/json')



