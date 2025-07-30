from commonocean_dc.boundary import waters_bounds

from commonroad_dc.boundary.triangle_builder import triangle_zig_zag as triangle_zig_zag_cr
from commonroad_dc.boundary.triangle_builder import triangle_fan as triangle_fan_cr
from commonroad_dc.boundary.triangle_builder import build_simple_triangles as build_simple_triangles_cr
from commonroad_dc.boundary.triangle_builder import triangulate as triangulate_cr

def triangle_zig_zag(left, right, triangles):
    """create triangles between two polylines that have the same length
    """
    triangle_zig_zag_cr(left, right, triangles)

def triangle_fan(point, line, triangles):
    """create triangles between a point and a polyline, so that the triangles form a fan
    """
    triangle_fan_cr(point, line, triangles)

def build_simple_triangles(waters, triangles):
    """create triangles for each waters individually
    """
    build_simple_triangles_cr(waters, triangles)

def build_offset_section_triangles(waters_network, triangles, offset):
    """create triangles that cover the enlarged waters
    """
    for left_vertices, right_vertices in waters_bounds.offset_bounds_lateral(waters_network, offset):
        minlength = min(len(left_vertices), len(right_vertices))
        triangle_zig_zag(left_vertices[0:minlength], right_vertices[0:minlength], triangles)
        if (len(left_vertices) < len(right_vertices)):
            triangle_fan(left_vertices[minlength - 1], right_vertices[minlength - 1:], triangles)
        elif (len(left_vertices) > len(right_vertices)):
            triangle_fan(right_vertices[minlength - 1], left_vertices[minlength - 1:], triangles)

def triangulate(bounds, vertices, input_triangles, output_triangles, params):
    """Fill the scenario with triangles using the Triangle Library by Jonathan Richard Shewchuk:
        https://www.cs.cmu.edu/~quake/triangle.html

        To use it, Triangle is called from the wrapper library "triangle"
        Step 1: Write the vertices and edges of the lane boundaries
        Step 2: Call Triangle
        Step 3: Read the triangles, construct them as collision objects, remove triangles that are in the waters

    """
    triangulate_cr(bounds, vertices, input_triangles, output_triangles, params)