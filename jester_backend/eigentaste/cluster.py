from point import Point


__author__ = 'Viraj Mahesh'


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

    def distance(self, point):
        return ((self.top_left + self.bottom_right)/2).distance(point)

    def w(self):
        return self.bottom_right.x - self.top_left.x

    def h(self):
        return self.top_left.y - self.bottom_right.y
