import numpy as np
from pprint import pprint


__author__ = 'Viraj Mahesh'


class ItemCluster(object):

    def __init__(self, indices=None, predictions=None):
        if indices is None or predictions is None:
            return
        self.indices = [idx for idx, val in enumerate(indices) if val]
        self.jokes = len(self.indices)
        self.predictions = predictions[:, self.indices]
        self.prediction_order = self.generate_prediction_order()
        self.averages = np.nanmean(self.predictions, axis=1)

    def export_model(self):
        exported_item_cluster = {'indices': self.indices,
                                 'jokes': int(self.jokes),
                                 'predictions': self.predictions.tolist(),
                                 'prediction order': self.prediction_order.tolist(),
                                 'averages': self.averages.tolist()}
        return exported_item_cluster

    @classmethod
    def import_model(cls, model):
        item_cluster = cls()
        item_cluster.indices = np.array(model['indices'])
        item_cluster.jokes = model['jokes']
        item_cluster.predictions = np.array(model['predictions'])
        item_cluster.prediction_order = np.array(model['prediction order'])
        item_cluster.averages = np.array(model['averages'])
        return item_cluster

    def recommend(self, user_cluster_id, jokes_rated):
        return self.indices[
            self.prediction_order[user_cluster_id][-jokes_rated - 1]
        ]

    def moving_averages(self, cluster_idx):
        return self.averages[cluster_idx]

    def generate_prediction_order(self):
        return np.argsort(self.predictions, axis=1)

    def __repr__(self):
        return 'ItemCluster(items={0})'.format(self.jokes)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()