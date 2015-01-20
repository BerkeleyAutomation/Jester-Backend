__author__ = 'Viraj Mahesh'

from sklearn.preprocessing import Imputer
from sklearn.decomposition import PCA

class Eigentaste(object):
    def __init__(self, train, gauge):
        """
        Initializes Eigentaste with a training set and gauge set.
        :param train: The dataset on which Eigentaste must be trained.
        :param gauge: List of indices that define the gauge set.
        :return: None
        """
        # Store training data and gauge set
        self.train = train
        self.gauge = gauge
        # Impute missing values using mean imputation
        self.imputed_train = Imputer().fit_transform(train)
        # Create a new PCA model and fit it to the training data (gauge set
        # sub-matrix). The PCA model will be used to project new users into the
        # same plane as the rest of the data set.
        self.pca_model = PCA()
        self.pca_data = self.pca_model.fit_transform(train[:, gauge])

    def _create_clusters(self):
        # Transpose data so that X and Y components are rows
        x, y = self.pca_data.T



class Cluster(object):
    def __init__(self, top_left):


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

