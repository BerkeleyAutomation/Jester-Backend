from __future__ import division
from django.http import HttpResponse
from jester.models import *
from distutils.util import strtobool
from datetime import datetime
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
    if filter_null is True:
        ratings = filter(lambda x: x != 0, ratings)
    bins, width = 20, 1  # Hardcoded number of bins. Works better
    hist, bin_edges = np.histogram(ratings, bins=bins)
    hist, bin_edges = hist.tolist(), bin_edges.tolist()
    response = {
        'heights': zip(np.add(bin_edges, width/2), hist),
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
            'mean': np.mean(ratings)
        }
    }
    return HttpResponse(HttpResponse(json.dumps(response),
                                     content_type="application/json"))
