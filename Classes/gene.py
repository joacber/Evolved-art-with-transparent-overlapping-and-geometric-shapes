from random import *
import numpy as np


# generates an value between 0 and 255, to be used as red, green or blue value.
def generate_color():
    return randint(0, 256)


# generates an value between 0 and 1 with 4 decimals to be used as alpha value.
def generate_alpha():
    return round(uniform(0, 1), 4)


def generate_radius(self):
    return randint(1, int(self.width / 2))


# generates a coordinate to be used as center for the circle.
def generate_point_coordinate(self):
    return randint(0, self.width), randint(0, self.height)


# generates coordinates for each vertices, in the for of an numpy array.
def generate_polygon_coordinates(self):
    pts = []
    for j in range(self.vertices):
        pts = pts + [([randint(0, self.width), randint(0, self.height)])]
    return np.array(pts)


def generate_thickness():
    return randint(1, 20)


class Polygon:
    def __init__(self, vertices, width, height):
        self.vertices = vertices
        self.width = width
        self.height = height

        self.color = (generate_color(), generate_color(), generate_color())
        self.alpha = generate_alpha()
        self.coordinates = generate_polygon_coordinates(self)
        # self.mutate_record = []

    def __repr__(self) -> str:
        return "%s , %s ,\n %s" % (self.color, self.alpha, self.coordinates)


class Circle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.color = (generate_color(), generate_color(), generate_color())
        self.alpha = generate_alpha()
        self.coordinates = generate_point_coordinate(self)
        self.radius = generate_radius(self)
        # self.mutate_record = []

    def __repr__(self) -> str:
        return "%s , %s , \n%s , %s" % (self.color, self.alpha, self.coordinates, self.radius)


class Line:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.color = (generate_color(), generate_color(), generate_color())
        self.alpha = generate_alpha()
        self.coordinates = generate_point_coordinate(self)
        self.coordinates_to = generate_point_coordinate(self)
        self.thickness = generate_thickness()
        # self.mutate_record = []

    def __repr__(self) -> str:
        return "%s , %s , \n%s , %s" % (self.color, self.alpha, self.coordinates, self.thickness)
