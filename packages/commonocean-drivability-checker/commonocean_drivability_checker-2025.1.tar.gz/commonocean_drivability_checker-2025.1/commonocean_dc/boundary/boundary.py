from commonocean.scenario.scenario import Scenario

from commonocean_dc.boundary import construction

from commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch import create_collision_checker, create_collision_object

def create_waters_boundary_obstacle(scenario: Scenario, method='triangulation', return_scenario_obstacle=True, **kwargs):
    """
    Creates the waters boundary for the given scenario.

    :param scenario: the input scenario to be triangulated
    :param method: waters boundary creation method: triangulation - Delaunay triangulation, aligned_triangulation - axis-aligned triangles using GPC polygon strips, obb_rectangles - OBB rectangles on the waters border (default: triangulation)
    :param return_scenario_obstacle: additionally create a commonwaters StaticObstacle for the waters boundary
    :param kwargs: settings of the method
    :return: [optional: StaticObstacle representing the waters boundary,] ShapeGroup with the collision checker objects

    Available methods:

    -triangulation

    Delaunay triangulation

    -aligned_triangulation

    Divides the polygons representing the waters boundary into axis-aligned tiles and triangulates the tiles separately into the triangles having one side parallel to the other axis (in order to reduce the number of candidate triangles for collision checks).

    Settings:

    axis - 0: Use vertical tiles, 1: Use horizontal tiles, 'auto': Use horizontal tiles if width<height.

    boundary_margin - Size of margin for the calculation of scenario corners.

    -obb_rectangles

    In contrast to triangulation, this method creates a set of oriented rectangles that separates the waters and the waters boundary.
    To compute the set, we first compute the union of all waters in the waters network and then extract the inner and outer contours of the resulting polygon.
    Afterwards, we create an oriented rectangle for each line segment of the inner and outer contours.
    The oriented rectangles symmetrically overapproximate each line segment.
    In this way, we can reduce the false positive rate at waters forks and merges.

    Settings:

    width: Width of the generated rectangles. Default: 1e-5.

    Example:

    create_waters_boundary_obstacle(scenario, method = 'aligned_triangulation', axis='auto')

    """

    boundary = construction.construct_boundary_obstacle(scenario, method, return_scenario_obstacle, kwargs)
    return boundary


def create_waters_polygons(scenario: Scenario, method='lane_polygons', **kwargs):
    """
    Creates a ShapeGroup with collision checker polygons representing the waters.

    :param scenario: the input scenario for the creation of waters polygons
    :param method: waters polygons creation method: lane_polygons - lane polygons, waters_polygons - waters polygons, whole_polygon - whole polygon, whole_polygon_tiled - whole polygon subdivided into tiles (default: lane_polygons)
    :param kwargs: settings of the method
    :return: ShapeGroup with the collision checker polygons

    Available methods:

    -lane_polygons

    Creates lane polygons for the given scenario. Optionally uses Douglas-Peucker resampling and buffering of the polygons.

    Settings:

    resample - use Douglas-Peucker resampling. 0 - no resampling, 1 - enable resampling.

    resample_tolerance_distance - tolerance distance for the resampling (default: 2e-5).

    buffer - use polygon buffering. 0 - no buffering, 1 - enable buffering. The Boost Geometry library, mitre joins and flat ends are used for the buffering.

    buf_width - buffer width by which the resulting polygons should be enlarged (default: 5e-5).

    triangulate - True: triangles will be generated for the interior of each lane polygon using GPC Polygon strips, False: two triangles will be created for each lane polygon from its AABB bounding box.

    -waters_polygons

    Creates waters polygons for the given scenario. Optionally uses Douglas-Peucker resampling and buffering of the polygons.

    Settings:

    resample - use Douglas-Peucker resampling. 0 - no resampling, 1 - enable resampling.

    resample_tolerance_distance - tolerance distance for the resampling (default: 2e-5).

    buffer - use polygon buffering. 0 - no buffering, 1 - enable buffering. The Boost Geometry library, mitre joins and flat ends are used for the buffering.

    buf_width - buffer width by which the resulting polygons should be enlarged (default: 5e-5).

    triangulate - True: triangles will be generated for the interior of each waters polygon using GPC Polygon strips, False: two triangles will be created for each waters polygon from its AABB bounding box.

    -whole_polygon

    Creates large polygon(s), possibly with holes, representing the waters network for the given scenario.

    Settings:

    triangulate - True: triangles will be generated for the interior of each resulting polygon using GPC Polygon strips, False: two triangles will be created for each resulting polygon from its AABB bounding box.

    -whole_polygon_tiled

    Creates large polygon(s), possibly with holes, representing the scenario waters network. After that, tiles the polygon(s) into uniform rectangular grid cells.
    For the creation of polygon tiles, the uniform grid cells used are enlarged by epsilon to avoid any gaps between the generated polygon tiles.

    Settings:

    max_cell_width - maximal grid cell width.

    max_cell_height - maximal grid cell height.

    triangulate - True: triangles will be generated for the interior of each resulting polygon using GPC Polygon strips, False: two triangles will be created for each resulting polygon from its AABB bounding box.

    Example:

    create_waters_polygons(scenario, method = 'lane_polygons', resample=1, buffer=1, triangulate=True)

    """

    boundary = construction.construct_waters_polygons(scenario, method, kwargs)
    return boundary

def create_shallow_polygons(scenario: Scenario, method='lane_polygons', **kwargs):
    shallow_occupancy = construction.construct_shallow_polygons(scenario, method, kwargs)
    return shallow_occupancy

def overlapping_shallow_waters(scenario: Scenario, method_waters='lane_polygons', method_shallow = 'lane_polygons', **kwargs):
    navigable_waters = construction.construct_waters_polygons(scenario, method_waters, kwargs)
    shallow = construction.construct_shallow_polygons(scenario, method_shallow, kwargs)
    return navigable_waters.collide(shallow), [navigable_waters, shallow]

def has_enough_depth(scenario: Scenario, main_obj = None, standard_depth=15, method='lane_polygons', **kwargs):
    """

    Function that checks if a certain trajectory or dynamic obstacle is compatible with the depth of the environment path.
    It can be called with a simple trajectory (and a manually chosen depth, as the trajectory calls does not have its own depth) or even with a proper dynamic obstacle object and its own depth.
    Remember that the Waterways themselves have infinite depth.

    :param scenario: the input scenario to be considered
    :param main_obj: object to be tested (can be a trajectory or even a dynamic obstacle)
    :param standard_depth: standard depth to be compared to, in case the main object does not have an intrinsic value (if it is not an obstacle)
    :param method: method used to construct the shallows polygons
    :param kwargs: extra standard arguments used in the construction of the shallow polygons 

    :return: flag (bool) indicating if the depth is safe for that path, [entire shallow polygon or shallow that collided, collision main object]

    Available methods:

    - lane_polygons
    - whole_polygon
    - whole_polygon_tiled

    Example:

    has_enough_depth(scenario, trajectory, standard_depth = 25, method = 'lane_polygons')

    """

    if main_obj:
        whole_scenario = create_collision_checker(scenario)
        shallow = construction.construct_shallow_polygons(scenario, method, kwargs)
        obj = create_collision_object(main_obj)

        try:
            depth = main_obj.depth
        except:
            print("Your object does not have a depth value, we used the standard value to compare (modify it through standard_depth)")
            depth = standard_depth

        if whole_scenario.collide(obj):

            collide_flag = False
            for obs in scenario.static_obstacles:
                if obj.collide(create_collision_object(obs)):
                    collide_flag = True
            for obs in scenario.dynamic_obstacles:
                if obj.collide(create_collision_object(obs)):
                    collide_flag = True

            if collide_flag:
                print("Your object is colliding with other non-shallow objects!")
                return False, None
            else:
                for testing_shallow in scenario.shallows:
                    c_testing_shallow = create_collision_object(testing_shallow)
                    if c_testing_shallow.collide(obj):
                        if depth >= testing_shallow.depth:
                            return False, [c_testing_shallow, obj]
                        else:
                            pass
                    else:
                        pass
                return True, [shallow, obj]
        else:
            return True, [shallow, obj]
    else:
        print("Please insert an object to be tested!")
        return False, None
