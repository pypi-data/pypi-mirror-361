from commonroad_dc.boundary.scenario_bounds import calc_corners as calc_corners_cr
from commonroad_dc.boundary.scenario_bounds import calc_boundary_box as calc_boundary_box_cr

def calc_corners(waters, boundary_margin=20):
    """calculate the corners of the scenario from the waters
        corners: outermost coordinates in x and y direction:
        corners = [xmin, xmax, ymin, ymax]
    """
    return calc_corners_cr(waters, boundary_margin)


def calc_boundary_box(corners):
    """calculates the coordinates needed to build an axis aligned rectangle which spans the corners
        coordinates: width/2, height/2, center x, center y
    """
    return calc_boundary_box_cr(corners)
