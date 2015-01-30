from __future__ import division
import numpy as np
from math import sqrt
from sklearn.preprocessing import Imputer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


__author__ = 'Viraj Mahesh'


MISSING_JOKES = np.array([1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 14, 20, 27,
                          31, 43, 51, 52, 61, 73, 80, 100, 116])
NUM_JOKES = 150
JOKE_CLUSTERS = 15


class Eigentaste(object):
    def __init__(self, train, gauge, levels=4):
        """
        Initializes Eigentaste with a training set and gauge set.
        :param train: The dataset on which Eigentaste must be trained.
        :param gauge: List of indices that define the gauge set.
        :param levels: The number of recursive levels for user clustering.
        :param n_clusters: The number of cluster to partition jokes into.
        :return: None
        """
        # Store training data and gauge set
        self.train = np.delete(train, MISSING_JOKES - 1, axis=1)
        self.gauge = gauge
        self.levels = levels
        # Impute missing values using mean imputation
        self.imputed_train = Imputer().fit_transform(self.train)
        # Create a new PCA model and fit it to the training data (gauge set
        # sub-matrix). The PCA model will be used to project new users into the
        # same plane as the rest of the data set.
        self.gauge_set_submatrix = self.imputed_train[:, gauge]
        self.pca_model = PCA()
        self.pca_data = self.pca_model.fit_transform(self.gauge_set_submatrix)
        self.clusters = self._create_clusters()
        self.n_clusters = len(self.clusters)
        self.indices = self._classify()
        self._generate_predictions()
        self.kmeans_model = KMeans(n_clusters=JOKE_CLUSTERS)
        self.joke_cluster_indices = self._create_joke_clusters()

    def _create_clusters(self):
        """
        Creates a list of clusters by recursively bisecting those clusters that
        touch the origin
        """
        # Transpose data so that X and Y components are rows
        x, y = self.pca_data.T
        top_left = Point(np.min(x), np.max(y))
        bottom_right = Point(np.max(x), np.min(y))
        origin = (top_left + bottom_right)/2
        # Compute the bounding cluster which encompasses all the points in the
        # training set. The initial set of clusters is the set of 4 clusters
        # formed by the bisection of the bounding cluster.
        clusters = Cluster(top_left, bottom_right).bisect()
        # Recursively split the clusters
        for _ in range(self.levels):
            new_clusters = []
            for cluster in clusters:
                # Only split the cluster if one of the vertices is the origin
                if cluster.touches(origin):
                    new_clusters.extend(cluster.bisect())
                else:
                    new_clusters.append(cluster)
            # Repeat again with the newly created list of clusters
            clusters = new_clusters
        # Return the list of clusters
        return clusters

    def _create_joke_clusters(self):
        """
        Fits the kmeans model to the training set, creates joke (i.e item)
        clusters and returns a vector containing the cluster index of each joke.
        """
        return self.kmeans_model.fit_predict(self.imputed_train.T)

    def _classify(self):
        """
        Classify users in the training set by assigning them to one of the clusters.
        """
        indices = []
        # Iterate through all users in the training set and assign them to clusters
        for user in self.pca_data:
            point = Point(*user)
            # Iterate through each cluster to see if user is in the cluster
            for idx, cluster in enumerate(self.clusters):
                if point in cluster:
                    indices.append(idx)
                    break
        # Convert to a numpy array for efficient operations
        return np.array(indices)

    def _generate_predictions(self):
        for idx, cluster in enumerate(self.clusters):
            users = self.train[self.indices == idx]
            predicted_ratings = np.nanmean(users, axis=0).tolist()
            cluster.store_predictions(predicted_ratings)

    def get_joke_cluster_idx(self, idx):
        return self.joke_cluster_indices[idx]


class Point(object):
    """
    Represents a point in 2D space.
    """
    def __init__(self, x, y):
        """
        Create a new point.
        :param x: The x coordinate of the point
        :param y: The y coordinate of the point
        """
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __div__(self, other):
        return Point(self.x/other, self.y/other)

    def __truediv__(self, other):
        return self.__div__(other)

    def _approx_equal(self, a, b, tolerance=10**-6):
        """
        Checks if two floating point numbers are approximately equal, given a
        certain tolerance.
        """
        return abs(a - b) <= tolerance

    def __eq__(self, other):
        """
        Returns true if two points are equal. Points are equal if their
        x and y coordinates are approximately equal.
        """
        return self._approx_equal(self.x, other.x) and \
               self._approx_equal(self.y, other.y)

    def __repr__(self):
        return '({0}, {1})'.format(self.x, self.y)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

    def distance(self, point):
        return sqrt((self.x - point.x) ** 2 + (self.y - point.y) ** 2)


class Cluster(object):
    """
    Represents a rectangular cluster in 2D space. Clusters are denoted by the
    coordinates of the top left and bottom right corners.
    """
    def __init__(self, top_left, bottom_right):
        """
        Create a new cluster.
        :param top_left: The top left corner of the cluster.
        :param bottom_right: The bottom right corner of the cluster.
        """
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.predictions = {}

    def bisect(self):
        """
        Splits the cluster into 4 equal sized sub-clusters
        :return: A list containing the 4 equal sized sub-clusters of this cluster
        """
        # Calculate midpoint of the cluster
        mid = (self.top_left + self.bottom_right)/2
        # Calculate midpoints of all edges of the cluster
        mid_top_edge = Point(mid.x, self.top_left.y)
        mid_bottom_edge = Point(mid.x, self.bottom_right.y)
        mid_left_edge = Point(self.top_left.x, mid.y)
        mid_right_edge = Point(self.bottom_right.x, mid.y)
        # Return the 4 sub clusters formed from dividing this cluster
        return [Cluster(self.top_left, mid),
                Cluster(mid, self.bottom_right),
                Cluster(mid_top_edge, mid_right_edge),
                Cluster(mid_left_edge, mid_bottom_edge)]

    def __repr__(self):
        return '({0}, {1})'.format(self.top_left, self.bottom_right)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

    def touches(self, point):
        """
        :param point: The point we are checking.
        :return: True if point is one of the 4 corners of the clusters
        """
        bottom_left = Point(self.top_left.x, self.bottom_right.y)
        top_right = Point(self.bottom_right.x, self.top_left.y)
        return self.top_left == point or self.bottom_right == point or \
            bottom_left == point or top_right == point

    def __contains__(self, item):
        return self.top_left.x <= item.x <= self.bottom_right.x and \
               self.bottom_right.y <= item.y <= self.top_left.y

    def store_predictions(self, predictions):
        idx = 0
        for i in range(NUM_JOKES):
            if i + 1 in MISSING_JOKES:
                continue
            self.predictions[i] = predictions[idx]
            idx += 1

    def distance(self, point):
        return ((self.top_left + self.bottom_right)/2).distance(point)

    def w(self):
        return self.bottom_right.x - self.top_left.x

    def h(self):
        return self.top_left.y - self.bottom_right.y