import numpy as np

from commonroad_dc.geometry.util import chaikins_corner_cutting as chaikins_corner_cutting_cr
from commonroad_dc.geometry.util import resample_polyline as resample_polyline_cr
from commonroad_dc.geometry.util import resample_polyline_with_length_check as resample_polyline_with_length_check_cr
from commonroad_dc.geometry.util import compute_pathlength_from_polyline as compute_pathlength_from_polyline_cr
from commonroad_dc.geometry.util import compute_polyline_length as compute_polyline_length_cr
from commonroad_dc.geometry.util import compute_curvature_from_polyline as compute_curvature_from_polyline_cr
from commonroad_dc.geometry.util import compute_orientation_from_polyline as compute_orientation_from_polyline_cr


def chaikins_corner_cutting(polyline: np.ndarray, refinements: int = 1) -> np.ndarray:
    """
    Chaikin's corner cutting algorithm to smooth a polyline by replacing each original point with two new points.
    The new points are at 1/4 and 3/4 along the way of an edge.

    :param polyline: polyline with 2D points
    :param refinements: how many times apply the chaikins corner cutting algorithm
    :return: smoothed polyline
    """
    return chaikins_corner_cutting_cr(polyline, refinements)


def resample_polyline(polyline: np.ndarray, step: float = 2.0) -> np.ndarray:
    """
    Resamples point with equidistant spacing.

    :param polyline: polyline with 2D points
    :param step: sampling interval
    :return: resampled polyline
    """
    return resample_polyline_cr(polyline, step)


def resample_polyline_with_length_check(polyline, length_to_check: float = 2.0):
    """
    Resamples point with length check.
    TODO: This is a helper functions to avoid exceptions during creating CurvilinearCoordinateSystem

    :param polyline: polyline with 2D points
    :return: resampled polyline
    """
    return resample_polyline_with_length_check_cr(polyline, length_to_check)


def compute_pathlength_from_polyline(polyline: np.ndarray) -> np.ndarray:
    """
    Computes the path length of a given polyline

    :param polyline: polyline with 2D points
    :return: path length of the polyline
    """
    return compute_pathlength_from_polyline_cr(polyline)


def compute_polyline_length(polyline: np.ndarray) -> float:
    """
    Computes the length of a given polyline
    :param polyline: The polyline
    :return: The path length of the polyline
    """
    return compute_polyline_length_cr(polyline)


def compute_curvature_from_polyline(polyline: np.ndarray) -> np.ndarray:
    """
    Computes the curvature of a given polyline

    :param polyline: The polyline for the curvature computation
    :return: The curvature of the polyline
    """
    return compute_curvature_from_polyline_cr(polyline)


def compute_orientation_from_polyline(polyline: np.ndarray) -> np.ndarray:
    """
    Computes the orientation of a given polyline

    :param polyline: polyline with 2D points
    :return: orientation of polyline
    """
    return compute_orientation_from_polyline_cr(polyline)
