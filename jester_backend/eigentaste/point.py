from math import sqrt

__author__ = 'Viraj Mahesh'


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
