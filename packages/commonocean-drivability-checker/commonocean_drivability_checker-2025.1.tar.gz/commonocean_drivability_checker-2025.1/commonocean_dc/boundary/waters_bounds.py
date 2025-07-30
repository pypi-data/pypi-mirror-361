import numpy as np

from commonocean_dc.boundary import rectangle_builder

from commonroad_dc.boundary.lanelet_bounds import polyline_normals as polyline_normals_cr
from commonroad_dc.boundary.lanelet_bounds import polyline_edges as polyline_edges_cr
from commonroad_dc.boundary.lanelet_bounds import pairs as pairs_cr
# from commonroad_dc.boundary.lanelet_bounds import longitudinal_bounds as longitudinal_bounds_cr
# from commonroad_dc.boundary.lanelet_bounds import lane_hull as lane_hull_cr


def lateral_bounds(waters_networks):
    """generator function to find the leftmost and rightmost boundaries of each lane section
        the vertices and the boundaries are ordered in the same direction
    """
    waters = waters_networks.waterways
    waters_id_list = list(map(lambda l: l.waters_id, waters))
    while waters_id_list != []:
        # search for the leftmost and rightmost waters adjacent to the current one
        id = waters_id_list.pop()
        right = left = waters_networks.find_waterway_by_id(id)
        right_direction = left_direction = True


        if (left_direction):
            left_vertices = left.left_vertices
        else:
            # vertices are in a coloumn vector, flipud to reverse the order of the vertices
            left_vertices = np.flipud(left.right_vertices)

        if (right_direction):
            right_vertices = right.right_vertices
        else:
            right_vertices = np.flipud(right.left_vertices)

        yield left_vertices, right_vertices


def longitudinal_bounds(waters):
    """ generator function to find the first and last boundaries of successive waters
    """
    for l in waters:
        left = l.left_vertices
        right = l.right_vertices
        if l.predecessor == []:
            yield left[0], right[0]
        if l.successor == []:
            yield left[-1], right[-1]



def lane_sections(fairway_network):
    """ generator function that generates the boundaries of each lane section

        creates the left and right bounds like longitudinal_bounds(), but also generates the polylines at the
        start and end of each lane section. These can be used for delaunay triangulation of a lane section, which
        leads to a perfect collision representation of a lane.

        yields the boundary of each lane section as four polylines, namely:
        start_vertices, left_vertices, end_vertices, right_vertices
    """
    fairways = fairway_network.waterways
    fairway_id_list = list(map(lambda f: f.waters_id, fairways))

    while fairway_id_list != []:
        # search for the leftmost and rightmost waters adjacent to the current one
        id = fairway_id_list.pop()
        current = fairway_network.find_waterway_by_id(id)
        direction = True

        start_vertices = []
        end_vertices = []

        def add_initial_lateral_vertices(current, direction):
            if direction:
                start_vertices.append(current.right_vertices[0])
                end_vertices.insert(0, current.right_vertices[-1])
            else:
                start_vertices.append(current.left_vertices[-1])
                end_vertices.insert(0, current.left_vertices[0])

        def add_lateral_vertices(current, direction):
            if direction:
                start_vertices.append(current.left_vertices[0])
                end_vertices.insert(0, current.left_vertices[-1])
            else:
                start_vertices.append(current.right_vertices[-1])
                end_vertices.insert(0, current.right_vertices[0])

        if direction:
            right_vertices = np.flipud(current.right_vertices)
        else:
            right_vertices = current.left_vertices

        add_initial_lateral_vertices(current, direction)
        add_lateral_vertices(current, direction)

        if direction:
            left_vertices = current.left_vertices
        else:
            # vertices are in a coloumn vector, flipud to reverse the order of the vertices
            left_vertices = np.flipud(current.right_vertices)

        start_vertices = np.array(start_vertices)
        end_vertices = np.array(end_vertices)
        print(f"start: {start_vertices},left: {left_vertices},end: {end_vertices},right: {right_vertices}")
        yield start_vertices, left_vertices, end_vertices, right_vertices


def lane_hull(waters_networks):
    """Yields the single polyline which describes the boundary of each lane section"""
    for start_vertices, left_vertices, end_vertices, right_vertices in lane_sections(waters_networks):
        # the corner vertices are included twice
        yield np.concatenate((start_vertices, left_vertices[1:-1], end_vertices, right_vertices[1:-1]))


def offset_bounds(waters_networks, offset):
    """generator function that generates the lateral and longitudinal boundaries
        and moves them to the outside by the offset value
    """

    def elongate_line(v, w):
        """move both points which form a line, so that the line is elongated by offset*2"""
        if np.linalg.norm(w - v) == 0:
            return v, w
        tangent = offset * (w - v) / np.linalg.norm(w - v)
        return v - tangent, w + tangent

    def elongate_boundary(bound):
        """insert points at the beginning and end, so that the boundary is elongated"""
        bound = np.insert(bound, 0, elongate_line(*bound[:2])[0], axis=0)
        # had problems with np.append, so use of insert at len - 1
        return np.insert(bound, len(bound), elongate_line(*bound[-2:])[1], axis=0)

    # TODO: reduce, special case of elongate_line
    def offset_point(v, w):
        """offset point v away from point w"""
        tangent = offset * (w - v) / np.linalg.norm(w - v)
        return v - tangent

    def offset_bound_rel_other(bound, other):
        """offset a boundary relative to another, which is opposite to it"""

        def offset_point_rel_other(v):
            """offset point away from closest point on the opposite boundary"""
            index = np.argmin([np.linalg.norm(w - v) for w in other])
            return offset_point(v, other[index])

        return np.apply_along_axis(lambda v: offset_point_rel_other(v), 1, bound)

    def longitudinal_bounds_offset(waters):
        """rewritten longitudinal_bounds function
            required because we need to know for each bound which waters it corresponds to"""
        for l in waters:
            left = l.left_vertices
            right = l.right_vertices
            if l.predecessor == []:
                v, w = elongate_line(left[0], right[0])
                v = offset_point(v, left[1])
                w = offset_point(w, right[1])
                yield np.array((v, w))
            if l.successor == []:
                v, w = elongate_line(left[-1], right[-1])
                v = offset_point(v, left[-2])
                w = offset_point(w, right[-2])
                yield np.array((v, w))
        return None

    for left_vertices, right_vertices in lateral_bounds(waters_networks):
        left_vertices = offset_bound_rel_other(left_vertices, right_vertices)
        left_vertices = elongate_boundary(left_vertices)

        right_vertices = offset_bound_rel_other(right_vertices, left_vertices)
        right_vertices = elongate_boundary(right_vertices)
        yield left_vertices
        yield right_vertices

    for bound in longitudinal_bounds_offset(waters_networks.waterways):
        yield bound


def offset_bounds_lateral(waters_networks, offset):
    """Same as offset_bounds, but returns only lateral bounds, in pairs (left,right)"""

    def elongate_line(v, w):
        """move both points which form a line, so that the line is elongated by offset*2"""
        if np.linalg.norm(w - v) == 0:
            return v, w
        tangent = offset * (w - v) / np.linalg.norm(w - v)
        return v - tangent, w + tangent

    def elongate_boundary(bound):
        """insert points at the beginning and end, so that the boundary is elongated"""
        bound = np.insert(bound, 0, elongate_line(*bound[:2])[0], axis=0)
        # had problems with np.append, so use of insert at len - 1
        return np.insert(bound, len(bound), elongate_line(*bound[-2:])[1], axis=0)

    # TODO: reduce, special case of elongate_line
    def offset_point(v, w):
        """offset point v away from point w"""
        tangent = offset * (w - v) / np.linalg.norm(w - v)
        return v - tangent

    def offset_bound_rel_other(bound, other):
        """offset a boundary relative to another, which is opposite to it"""

        def offset_point_rel_other(v):
            """offset point away from closest point on the opposite boundary"""
            index = np.argmin([np.linalg.norm(w - v) for w in other])
            return offset_point(v, other[index])

        return np.apply_along_axis(lambda v: offset_point_rel_other(v), 1, bound)

    for left_vertices, right_vertices in lateral_bounds(waters_networks):
        left_vertices = offset_bound_rel_other(left_vertices, right_vertices)
        left_vertices = elongate_boundary(left_vertices)

        right_vertices = offset_bound_rel_other(right_vertices, left_vertices)
        right_vertices = elongate_boundary(right_vertices)
        yield left_vertices, right_vertices


def outer_vertices(waters_networks, quads):
    """Generates all bounds that collide with the quads and are therefore considered to be outside
        Return: outer vertices in pairs
    """
    RECTANGLE_WIDTH = 0.2

    def iterate_vertices(vertices):
        v = vertices[0]
        for w in vertices[1:]:
            rect = rectangle_builder.get_rectangle(RECTANGLE_WIDTH, v, w)
            if rect.collide(quads):
                yield v, w
            v = w

    for leftvertices, rightvertices in lateral_bounds(waters_networks):
        yield from iterate_vertices(leftvertices)
        yield from iterate_vertices(rightvertices)
    for v1, v2 in longitudinal_bounds(waters_networks.waterways):
        yield from iterate_vertices([v1, v2])


def pairwise_bounds(waters_networks):
    """Yields the longitudinal and lateral bounds of the waters in the network in pairs"""
    for left_vertices, right_vertices in lateral_bounds(waters_networks):
        v1 = left_vertices[0]
        for v2 in left_vertices[1:]:
            yield v1, v2
            v1 = v2

        v1 = right_vertices[0]
        for v2 in right_vertices[1:]:
            yield v1, v2
            v1 = v2

    for bound in longitudinal_bounds(waters_networks.waterways):
        yield bound


def pairwise_offset_bounds(waters_networks, offset):
    """Yields the offset longitudinal and lateral bounds of the waters in the network in pairs"""
    for bound in offset_bounds(waters_networks, offset):
        v1 = bound[0]
        for v2 in bound[1:]:
            yield v1, v2
            v1 = v2


def pairs(l, cyclic=True):
    """
    Creates pairs of adjacent elements in l
    :param l: list
    :param cyclic: last and first element make a pair
    :return: iterator of pairs
    """
    return pairs_cr(l,cyclic)


def polyline_edges(polyline, cyclic=True):
    """Returns the edges between each two points of a polyline.

        cyclic: flags if there exists an edge between the last and first point
    """
    return polyline_edges_cr(polyline,cyclic)


def polyline_normals(polyline, cyclic=True):
    """Returns the normals of each points of a cyclic polyline.
    The sign of the normals can be seen as arbitrary,
    i.e. they do not necessarily point to the outwards of the polygon that the line describes.

    The normal for a point p at the index i s defined as following:
        normal = normal(p[i-1] - p[i]) + normal(p[i+1] - p[i])
    with all the involved normals being normalized.
    """
    return polyline_normals_cr(polyline, cyclic)