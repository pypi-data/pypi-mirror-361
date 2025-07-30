import commonroad.geometry.shape
import numpy as np
import shapely
from commonroad_dc.collision.collision_detection.minkowski_sum import minkowski_sum_circle as minkowski_sum_circle_cr
from commonroad_dc.collision.collision_detection.minkowski_sum import minkowski_sum_circle_shapely_polygon as minkowski_sum_circle_shapely_polygon_cr
from commonroad_dc.collision.collision_detection.minkowski_sum import minkowski_sum_circle_polygon as minkowski_sum_circle_polygon_cr
from commonroad_dc.collision.collision_detection.minkowski_sum import minkowski_sum_circle_circle as minkowski_sum_circle_circle_cr
from commonroad_dc.collision.collision_detection.minkowski_sum import minkowski_sum_circle_rectangle as minkowski_sum_circle_rectangle_cr
from commonroad_dc.collision.collision_detection.minkowski_sum import minkowski_sum_circle_shape_group as minkowski_sum_circle_shape_group_cr


def minkowski_sum_circle(shape: commonroad.geometry.shape.Shape,
                         radius: float, resolution: int) -> commonroad.geometry.shape.Shape:
    return minkowski_sum_circle_cr(shape, radius, resolution)

def minkowski_sum_circle_shapely_polygon(polygon: shapely.geometry.Polygon,
                                         radius: float, resolution: int) -> np.ndarray:
    """
    Computes the minkowski sum of a provided polygon and a circle with
    parametrized radius

    :param polygon: The polygon as a numpy array with columns as x and y
    coordinates
    :param radius: The radius of the circle
    :return: The minkowski sum of the provided polygon and the circle with the
    parametrized radius
    """
    return minkowski_sum_circle_shapely_polygon_cr(polygon, radius, resolution)


def minkowski_sum_circle_polygon(polygon: commonroad.geometry.shape.Polygon,
                                 radius: float, resolution: int) \
        -> commonroad.geometry.shape.Polygon:
    return minkowski_sum_circle_polygon_cr(polygon, radius, resolution)


def minkowski_sum_circle_circle(circle: commonroad.geometry.shape.Circle,
                                radius: float, resolution: int) \
        -> commonroad.geometry.shape.Circle:
    return minkowski_sum_circle_circle_cr(circle, radius, resolution)


def minkowski_sum_circle_rectangle(
        rectangle: commonroad.geometry.shape.Rectangle, radius: float, resolution: int) \
        -> commonroad.geometry.shape.Polygon:
    return minkowski_sum_circle_rectangle_cr(rectangle, radius, resolution)

def minkowski_sum_circle_shape_group(
        shape_group: commonroad.geometry.shape.ShapeGroup, radius: float, resolution: int) \
        -> commonroad.geometry.shape.ShapeGroup:
    return minkowski_sum_circle_shape_group_cr(shape_group, radius, resolution)