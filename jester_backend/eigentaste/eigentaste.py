from __future__ import division
import numpy as np
from sklearn.preprocessing import Imputer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from point import Point
from cluster import Cluster


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