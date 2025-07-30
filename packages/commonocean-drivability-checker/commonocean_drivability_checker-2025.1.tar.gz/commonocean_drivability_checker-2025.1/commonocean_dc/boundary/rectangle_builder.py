from commonroad_dc.boundary.rectangle_builder import get_rectangle as get_rectangle_cr

def get_rectangle(width, v1, v2):
    """builds a rectangle object which has the line v1,v2 as middle line"""
    return get_rectangle_cr(width, v1, v2)