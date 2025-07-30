import commonroad.geometry.shape
import commonocean.prediction
import commonocean.scenario.obstacle
import commonroad_dc.pycrcc as pycrcc
from commonocean.scenario.scenario import Scenario
import commonocean
from commonocean.scenario.scenario import Scenario
from commonocean.scenario.obstacle import *
from commonroad.geometry.shape import *

import commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch

from commonroad_dc.collision.collision_detection.scenario import create_collision_object_rectangle as create_collision_object_rectangle_cr
from commonroad_dc.collision.collision_detection.scenario import create_collision_object_circle as create_collision_object_circle_cr
from commonroad_dc.collision.collision_detection.scenario import create_collision_object_polygon as create_collision_object_polygon_cr


def create_collision_checker_scenario(scenario: Scenario, params=None, collision_object_func=None):
    cc = pycrcc.CollisionChecker()
    for co in scenario.dynamic_obstacles:
        cc.add_collision_object(commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch.
                                create_collision_object(co, params, collision_object_func))
    shape_group = pycrcc.ShapeGroup()
    for co in scenario.static_obstacles:
        collision_object = commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch. \
            create_collision_object(co, params, collision_object_func)
        if isinstance(collision_object, pycrcc.ShapeGroup):
            for shape in collision_object.unpack():
                shape_group.add_shape(shape)
        else:
            shape_group.add_shape(collision_object)
    cc.add_collision_object(shape_group)

    for shallow in scenario.shallows:
        cc.add_collision_object(commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch.
                                create_collision_object(shallow.shape, params, collision_object_func))

    return cc


def create_collision_object_rectangle(rect, params=None, collision_object_func=None):
    return create_collision_object_rectangle_cr(rect, params, collision_object_func)


def create_collision_object_circle(circle, params=None, collision_object_func=None):
    return create_collision_object_circle_cr(circle, params, collision_object_func)


def create_collision_object_polygon(polygon, params=None, collision_object_func=None):
    return create_collision_object_polygon_cr(polygon, params, collision_object_func)


def create_collision_object_shape_group(shape_group, params=None, collision_object_func=None):
    sg = pycrcc.ShapeGroup()
    for shape in shape_group.shapes:
        co = commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch.create_collision_object(
            shape, params, collision_object_func)
        if co is not None:
            sg.add_shape(co)
    return sg


def create_collision_object_static_obstacle(static_obstacle, params=None, collision_object_func=None):
    initial_time_step = static_obstacle.initial_state.time_step
    occupancy = static_obstacle.occupancy_at_time(initial_time_step)
    return commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch.create_collision_object(
        occupancy.shape, params, collision_object_func)

def create_collision_object_shallow(shallow, params=None, collision_object_func=None):
    return commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch.create_collision_object(
        shallow.shape, params, collision_object_func)


def create_collision_object_dynamic_obstacle(dynamic_obstacle, params=None, collision_object_func=None):
    initial_time_step = dynamic_obstacle.initial_state.time_step
    tvo = pycrcc.TimeVariantCollisionObject(initial_time_step)
    # add occupancy of initial state
    tvo.append_obstacle(commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch.create_collision_object(
        dynamic_obstacle.occupancy_at_time(initial_time_step).shape, params, collision_object_func))
    # add occupancies of prediction
    if dynamic_obstacle.prediction is not None:
        for occupancy in dynamic_obstacle.prediction.occupancy_set:
            tvo.append_obstacle(
                commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch.create_collision_object(
                    occupancy.shape, params, collision_object_func))
    return tvo


def create_collision_object_prediction(prediction, params=None, collision_object_func=None):
    tvo = pycrcc.TimeVariantCollisionObject(prediction.initial_time_step)
    for occupancy in prediction.occupancy_set:
        tvo.append_obstacle(
            commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch.create_collision_object(
                occupancy.shape, params, collision_object_func))
    return tvo


collision_object_func_dict = {
    commonroad.geometry.shape.ShapeGroup: create_collision_object_shape_group,
    commonroad.geometry.shape.Polygon: create_collision_object_polygon,
    commonroad.geometry.shape.Circle: create_collision_object_circle,
    commonroad.geometry.shape.Rectangle: create_collision_object_rectangle,
    commonocean.scenario.obstacle.StaticObstacle: create_collision_object_static_obstacle,
    commonocean.scenario.obstacle.DynamicObstacle: create_collision_object_dynamic_obstacle,
    commonocean.prediction.prediction.SetBasedPrediction: create_collision_object_prediction,
    commonocean.prediction.prediction.TrajectoryPrediction: create_collision_object_prediction,
    commonocean.scenario.obstacle.StaticObstacle: create_collision_object_static_obstacle,
    commonocean.scenario.obstacle.DynamicObstacle: create_collision_object_dynamic_obstacle,
    commonocean.scenario.waters.Shallow: create_collision_object_shallow,
    commonocean.prediction.prediction.TrajectoryPrediction: create_collision_object_prediction,
}

collision_checker_func_dict = {
    commonocean.scenario.scenario.Scenario: create_collision_checker_scenario,
    commonocean.scenario.scenario.Scenario: create_collision_checker_scenario
}
