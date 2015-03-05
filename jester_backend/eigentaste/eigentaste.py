from __future__ import division
import numpy as np
import json
import operator
from sklearn.preprocessing import Imputer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from point import Point
from item_cluster import ItemCluster
from jester import *
from jester.models import Joke
from cluster import Cluster


__author__ = 'Viraj Mahesh'


JOKE_CLUSTERS = 15
MOVING_AVERAGE_VECTOR_SIZE = 5


class Eigentaste(object):

    def __init__(self, train, gauge, levels=4):
        """
        Initializes Eigentaste with a training set and gauge set.

        :param train: The dataset on which Eigentaste must be trained.
        :param gauge: List of indices that define the gauge set.
        :param levels: The number of recursive levels for user clustering.
        :return: None
        """
        # Store training data and gauge set
        self.train = train
        self.gauge = gauge
        self.levels = levels

        # Store number of users and jokes
        self.users, self.jokes = self.train.shape

        # Impute missing values using mean imputation
        self.imputed_train = Imputer().fit_transform(self.train)

        # Create a new PCA model and fit it to the training data (gauge set
        # sub-matrix). The PCA model will be used to project new users into the
        # same plane as the rest of the data set.
        self.gauge_set_submatrix = self.imputed_train[:, gauge]
        self.pca_model = PCA()
        self.pca_data = self.pca_model.fit_transform(self.gauge_set_submatrix)

        # Split the projected data recursively into clusters
        self.clusters = self.create_clusters()
        # Assign the users to each cluster, generating a list of cluster indices
        self.indices = self.classify()
        # Generated the predicted value of joke ratings for each cluster
        self.predictions = self.calculate_predictions()

        # Split the jokes into joke clusters for dynamic recommendations
        self.kmeans_model = KMeans(n_clusters=JOKE_CLUSTERS)
        self.joke_clusters = self.create_joke_clusters()

    def create_clusters(self):
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

    def create_joke_clusters(self):
        """
        Fits the kmeans model to the training set, creates joke (i.e item)
        clusters and returns a vector containing the cluster index of each joke.
        """
        predictions = np.array(self.predictions)
        indices = self.kmeans_model.fit_predict(self.imputed_train.T)
        return [ItemCluster(indices == idx, predictions) for idx
                in range(JOKE_CLUSTERS)]

    def classify(self):
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

    def calculate_predictions(self):
        predictions = []
        for idx in range(len(self.clusters)):
            users = self.train[self.indices == idx]
            ratings = np.nanmean(users, axis=0).tolist()
            predictions.append(ratings)
        return predictions

    def export_model(self):
        pca_model = {'mean': self.pca_model.mean_.tolist(),
                     'components': self.pca_model.components_.tolist()}
        clusters = [cluster.export_model() for cluster in self.clusters]
        joke_clusters = [joke_cluster.export_model() for joke_cluster in
                         self.joke_clusters]
        exported_model = {'pca model': pca_model,
                          'user clusters': clusters,
                          'joke clusters': joke_clusters,
                          'predictions': self.predictions}
        return exported_model


class PCAModel(object):
    def __init__(self, model):
        self.mean = np.array(model['mean'])
        self.components = np.array(model['components'])

    def transform(self, user):
        user = np.array(user) - self.mean
        return np.dot(user, self.components.T)


class StoredEigentasteModel(object):
    def __init__(self, json_string):
        model = json.loads(json_string)
        self.pca_model = PCAModel(model['pca model'])
        self.clusters = [Cluster.import_model(cluster) for cluster in
                         model['user clusters']]
        self.joke_clusters = [ItemCluster.import_model(cluster) for cluster in
                              model['joke clusters']]
        self.predictions = model['predictions']

    def transform(self, user):
        return self.pca_model.transform(user)

    def classify(self, user):
        user = Point(*user)
        distances = [cluster.distance(user) for cluster in self.clusters]
        return np.argmin(distances)

    def moving_averages(self, cluster_idx):
        return [[cluster.moving_averages(cluster_idx)]
                * MOVING_AVERAGE_VECTOR_SIZE for cluster in self.joke_clusters]

    def recommend_joke(self, user):
        def all_rated(n):
            return user_model['jokes rated'][n] == self.joke_clusters[n].jokes

        user_model = user.load_model()
        moving_averages = user_model['moving averages']

        averages = [(idx, np.mean(ratings)) for idx, ratings in
                    enumerate(moving_averages) if not all_rated(idx)]

        item_cluster_idx, average = max(averages, key=operator.itemgetter(1))
        jokes_rated = user_model['jokes rated'][item_cluster_idx]
        user_cluster_idx = user_model['user cluster id']

        item_cluster = self.joke_clusters[item_cluster_idx]
        joke_id = item_cluster.recommend(user_cluster_idx, jokes_rated) + 1

        log_averages(user, averages)
        log_cluster_choice(user, item_cluster_idx, average)

        return Joke.objects.get(id=joke_id)

    def get_prediction(self, user, joke):
        user_model = user.load_model()
        cluster_id = user_model['user cluster id']
        return self.predictions[cluster_id][joke.id - 1]