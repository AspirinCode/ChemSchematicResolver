# -*- coding: utf-8 -*-
"""
Model for
========
Reading and writing images.
Editted from Matt Swains FDE model.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

log = logging.getLogger(__name__)

from . import decorators
import numpy as np

@decorators.python_2_unicode_compatible
class Rect(object):
    """A rectangular region."""

    def __init__(self, left, right, top, bottom):
        """

        :param int left: Left edge of rectangle.
        :param int right: Right edge of rectangle.
        :param int top: Top edge of rectangle.
        :param int bottom: Bottom edge of rectangle.
        """
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    @property
    def width(self):
        """Return width of rectangle in pixels. May be floating point value.

        :rtype: int
        """
        return self.right - self.left

    @property
    def height(self):
        """Return height of rectangle in pixels. May be floating point value.

        :rtype: int
        """
        return self.bottom - self.top

    @property
    def perimeter(self):
        """Return length of the perimeter around rectangle.

        :rtype: int
        """
        return (2 * self.height) + (2 * self.width)

    @property
    def area(self):
        """Return area of rectangle in pixels. May be floating point values.

        :rtype: int
        """
        return self.width * self.height

    @property
    def center(self):
        """Center point of rectangle. May be floating point values.

        :rtype: tuple(int|float, int|float)
        """
        xcenter = (self.left + self.right) / 2
        ycenter = (self.bottom + self.top) / 2
        return xcenter, ycenter

    @property
    def center_px(self):
        """(x, y) coordinates of pixel nearest to center point.

        :rtype: tuple(int, int)
        """
        xcenter, ycenter = self.center
        return np.around(xcenter), np.around(ycenter)

    def contains(self, other_rect):
        """Return true if ``other_rect`` is within this rect.

        :param Rect other_rect: Another rectangle.
        :return: Whether ``other_rect`` is within this rect.
        :rtype: bool
        """
        return (other_rect.left >= self.left and other_rect.right <= self.right and
                other_rect.top >= self.top and other_rect.bottom <= self.bottom)

    def overlaps(self, other_rect):
        """Return true if ``other_rect`` overlaps this rect.

        :param Rect other_rect: Another rectangle.
        :return: Whether ``other_rect`` overlaps this rect.
        :rtype: bool
        """
        return (min(self.right, other_rect.right) > max(self.left, other_rect.left) and
                min(self.bottom, other_rect.bottom) > max(self.top, other_rect.top))

    def separation(self, other_rect):
        """ Returns the distance between the center of each graph

        :param Rect other_rect: Another rectangle
        :return: Distance between centoids of rectangle
        :rtype: float
        """
        length = abs(self.center[0] - other_rect.center[0])
        height = abs(self.center[1] - other_rect.center[1])
        return np.hypot(length, height)


    def __repr__(self):
        return '%s(left=%s, right=%s, top=%s, bottom=%s)' % (
            self.__class__.__name__, self.left, self.right, self.top, self.bottom
        )

    def __str__(self):
        return '<%s (%s, %s, %s, %s)>' % (self.__class__.__name__, self.left, self.right, self.top, self.bottom)

class Panel(Rect):
    """ Tagged section inside Figure"""

    def __init__(self, left, right, top, bottom, tag):
        super(Panel, self).__init__(left, right, top, bottom)
        self.tag = tag
        self.repeating = False

    @property
    def repeating(self):
        return self.repeating

    @repeating.setter
    def repeating(self, repeating):
        self._repeating = repeating

class Diagram(Panel):
    """ Chemical Schematic Diagram that is identified"""

    def __init__(self, *args, label=None, smile=None):
        self._label = label
        self._smile = smile
        super(Diagram, self).__init__(*args)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def smile(self):
        return self._smile

    @smile.setter
    def smile(self, smile):
        self._smile = smile

    def __repr__(self):
        return '%s(label=%s, smile=%s' % (
            self.__class__.__name__, self.label.tag, self.smile
        )

    def __str__(self):
        return '<%s (%s, %s)>' % (self.__class__.__name__, self.label.tag, self.smile)



class Label(Panel):
    """ Label used as an identifier for the closest Chemical Schematic Diagram"""

    def __init__(self, *args):
        super(Label, self).__init__(*args)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

@decorators.python_2_unicode_compatible
class Figure(object):
    """A figure image."""

    def __init__(self, img, panels=None, plots=None, photos=None):
        """

        :param numpy.ndarray img: Figure image.
        :param list[Panel] panels: List of panels.
        :param list[Plot] plots: List of plots.
        :param list[Photo] photos: List of photos.
        """
        self.img = img
        self.width, self.height = img.shape[0], img.shape[1]
        self.center = (int(self.width * 0.5), int(self.height) * 0.5)
        self.panels = panels
        self.plots = plots
        self.photos = photos

        # TODO: Image metadata?

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def __str__(self):
        return '<%s>' % self.__class__.__name__

class Graph:
    """ Connected graph object
    Adapted from Neelan Yadav's code:
    https://www.geeksforgeeks.org/kruskals-minimum-spanning-tree-algorithm-greedy-algo-2"""

    def __init__(self, vertices):
        self.V = vertices # No. of vertices
        self.graph = [] # default dict for storing graph

    # Adds edge to graph
    def addEdge(self, u, v, w):
        self.graph.append([u, v, w])

    # Utility to find set of element i (using path compression techniques)
    def find(self, parent, i):
        if parent[i] == i:
            return i
        return self.find(parent, parent[i])

    # Does the union of 2 sets of x and y (by rank)
    def union(self, parent, rank, x, y):
        xroot = self.find(parent, x)
        yroot = self.find(parent, y)

        # Attach smaller rank tree under root of high rank tree
        if rank[xroot] < rank[yroot]:
            parent[xroot] = yroot
        elif rank[xroot] > rank[yroot]:
            parent[yroot] = xroot

        # If ranks are the same, make one as root and increment it's rank by one
        else:
            parent[yroot] = xroot
            rank[xroot] += 1

    # Main function, constructs minimum spanning tre by kruskals algorithm
    def kruskal(self):

        result = []

        i = 0 # Index for sorting edges
        e = 0  # Index for result

        # Step 1 : Sort edges in non-decreasing order of weight
        self.graph = sorted(self.graph, key=lambda item: item[2])

        parent, rank = [], []

        # Create V subsets with single elements
        for node in range(self.V):
            parent.append(node)
            rank.append(0)

        # Number of edges = V - 1
        while e < self.V - 1:

            # Step 2: Pick smallest dge, and increment index for next iteration
            u, v, w = self.graph[i]
            i += 1
            x = self.find(parent, u)
            y = self.find(parent, v)

            # If adding edges doesn't cause a cycle, include it in result and increment the index
            # Of the result for the next edge

            if x != y:
                e += 1
                result.append([u, v, w])
                self.union(parent, rank, x, y)

            # Else discard the edge

        return result

    def __str__(self):
        return '<%s : %s vertices >' % (self.__class__.__name__, self.V)



