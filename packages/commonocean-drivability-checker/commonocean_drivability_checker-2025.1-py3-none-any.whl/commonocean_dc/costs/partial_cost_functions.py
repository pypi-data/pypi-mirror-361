from typing import List, Dict, Any

import numpy as np
import os
import rules
import copy

from commonroad.common.util import Interval
from commonroad.geometry.shape import ShapeGroup, Rectangle
from commonocean.planning.planning_problem import PlanningProblem
from commonocean.scenario.waters import Waterway
from commonocean.scenario.scenario import Scenario
from commonocean.scenario.trajectory import Trajectory
from commonocean_dc.costs.route_matcher import SolutionProperties
from commonocean.prediction.prediction import TrajectoryPrediction
from commonocean.scenario.obstacle import ObstacleType, DynamicObstacle
from scipy.integrate import simpson

from rules.common.commonocean_evaluation_ship import CommonOceanObstacleEvaluation


from math import sin, cos, pi, atan2

class PartialCostFunctionException(Exception):
    pass


def euclidean_dist(x1: np.array, x2: np.array) -> float:
    """
    Returns the euclidean distance between two points.
    """
    return np.linalg.norm(x2 - x1)


def position_waters(scenario: Scenario, position: np.ndarray) -> List[Waterway]:
    """
    Returns the list of waters that contains the given position
    """
    position_waters_ids = scenario._waters_network.find_waterway_by_position(
        [position]
    )[0]
    position_waters = [
        scenario._waters_network.find_waters_by_id(waters_id)
        for waters_id in position_waters_ids
    ]
    return position_waters


def acceleration_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the acceleration cost for the given trajectory.
    """
    try:
        try:
            velocity = [float(((state.velocity)**2 + (state.velocity_y)**2)**(1/2)) for state in trajectory.state_list]
        except:
            velocity = [state.velocity for state in trajectory.state_list]
        acceleration = np.diff(velocity) / scenario.dt
        acceleration_sq = np.square(acceleration)
        cost = simpson(acceleration_sq, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of acceleration cost!"
        raise PartialCostFunctionException(msg) from ex


def jerk_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the jerk cost for the given trajectory.
    """
    try:
        velocity = [state.velocity for state in trajectory.state_list]
        acceleration = np.diff(velocity) / scenario.dt
        jerk = np.diff(acceleration) / scenario.dt
        jerk_sq = np.square(jerk)
        cost = simpson(jerk_sq, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of jerk cost!"
        raise PartialCostFunctionException(msg) from ex


def jerk_lat_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the lateral jerk cost for the given trajectory.
    """
    try:
        lat_jerk = [state.lat_jerk for state in trajectory.state_list]
        jerk_sq = np.square(lat_jerk)
        cost = simpson(jerk_sq, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of lateraljerk cost!"
        raise PartialCostFunctionException(msg) from ex


def jerk_lon_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the longitudinal jerk cost for the given trajectory.
    """
    try:
        lon_jerk = [state.lon_jerk for state in trajectory.state_list]
        jerk_sq = np.square(lon_jerk)
        cost = simpson(jerk_sq, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of longitudinal jerk cost!"
        raise PartialCostFunctionException(msg) from ex


def rudder_angle_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the rudder angle cost for the given trajectory.
    """
    try:
        rudder_angle = [state.rudder_angle for state in trajectory.state_list]
        rudder_angle_sq = np.square(rudder_angle)
        cost = simpson(rudder_angle_sq, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of rudder angle cost!"
        raise PartialCostFunctionException(msg) from ex


def rudder_rate_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the rudder rate cost for the given trajectory.
    """
    try:
        rudder_angle = [state.rudder_angle for state in trajectory.state_list]
        rudder_rate = np.diff(rudder_angle) / scenario.dt
        rudder_rate_sq = np.square(rudder_rate)
        cost = simpson(rudder_rate_sq, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of rudder rate cost!"
        raise PartialCostFunctionException(msg) from ex


def yaw_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the yaw cost for the given trajectory.
    """
    try:
        orientation = [state.orientation for state in trajectory.state_list]
        yaw_rate = np.diff(orientation) / scenario.dt
        yaw_rate_sq = np.square(yaw_rate)
        cost = simpson(yaw_rate_sq, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of yaw cost!"
        raise PartialCostFunctionException(msg) from ex


def path_length_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the path length cost for the given trajectory.
    """
    try:
        velocity = [state.velocity for state in trajectory.state_list]
        cost = simpson(velocity, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of path length cost!"
        raise PartialCostFunctionException(msg) from ex


def time_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the time cost for the given trajectory.
    """
    try:
        duration = (
            trajectory.state_list[-1].time_step - trajectory.state_list[0].time_step
        ) * scenario.dt
        return duration
    except Exception as ex:
        msg = f"An exception occurred during calculation of time cost!"
        raise PartialCostFunctionException(msg) from ex


def inverse_duration_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the inverse time cost for the given trajectory.
    """
    try:
        return 1 / min(
            time_cost(scenario, planning_problem, trajectory, properties), 0.1
        )  # in case trajectory has 0 ts
    except Exception as ex:
        msg = f"An exception occurred during calculation of inverse time cost!"
        raise PartialCostFunctionException(msg) from ex


def orientation_offset_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the Orientation Offset cost.

    """
    try:
        orientation_rel_lane_centers = np.square([s.delta_orientation for s in trajectory.state_list])
        cost = simpson(orientation_rel_lane_centers, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of orientation offset cost!"
        raise PartialCostFunctionException(msg) from ex


def velocity_offset_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the Velocity Offset cost.

    """
    try:
        goal_velocities = [
            goal_state.velocity.start
            if isinstance(goal_state.velocity, Interval)
            else goal_state.velocity
            for goal_state in planning_problem.goal.state_list
            if hasattr(goal_state, "velocity")
        ]
        goal_velocity = min(goal_velocities) if len(goal_velocities) > 0 else None

        velocity_diffs = []
        for state in trajectory.state_list:
            diff = goal_velocity - state.velocity if goal_velocity else 0
            velocity_diffs.append(diff)

        velocity_diffs_sq = np.square(velocity_diffs)
        cost = simpson(velocity_diffs_sq, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of velocity offset cost!"
        raise PartialCostFunctionException(msg) from ex


def longitudinal_velocity_offset_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the Velocity Offset cost.
    """

    #TODO: Correct implementation in the future (priority low since depends on complicated calculation of ref path)
    try:
        goal_velocities = [
            goal_state.velocity.start
            if isinstance(goal_state.velocity, Interval)
            else goal_state.velocity
            for goal_state in planning_problem.goal.state_list
            if hasattr(goal_state, "long_velocity")
        ]
        goal_velocity = min(goal_velocities) if len(goal_velocities) > 0 else None

        velocity_diffs = []
        for state in trajectory.state_list:
            diff = goal_velocity - state.long_velocity if goal_velocity else 0
            velocity_diffs.append(diff)

        velocity_diffs_sq = np.square(velocity_diffs)
        cost = simpson(velocity_diffs_sq, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of velocity offset cost!"
        raise PartialCostFunctionException(msg) from ex


def _get_shape_center(shape):
    if not isinstance(shape, ShapeGroup):
        return shape.center
    else:
        x = np.array([shape.center[0] for shape in shape.shapes])
        y = np.array([shape.center[1] for shape in shape.shapes])
    return np.array([np.mean(x), np.mean(y)])


def distance_to_obstacle_cost(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    """
    Calculates the Distance to Obstacle cost.
    """
    try:
        min_dists = []
        for state in trajectory.state_list:
            min_dists.append(np.min(properties[SolutionProperties.LonDistanceObstacles][state.time_step]))
        neg_min_dists = -0.2 * np.array(min_dists)
        exp_dists = np.array([np.math.exp(val) for val in neg_min_dists])
        cost = simpson(exp_dists, dx=scenario.dt)
        return cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of distance to obstacles cost!"
        raise PartialCostFunctionException(msg) from ex

def vcro(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    
    """
    Calculates the VCRO cost.
    """

    try:
        total_cost = 0
        trajectory_list = trajectory.state_list
        for dyn_obs in scenario.dynamic_obstacles:
            for ego_state in trajectory_list:

                obs_state = dyn_obs.state_at_time(ego_state.time_step)
                partial_cost = 0

                if obs_state is None:
                    pass
                else:
                    ego_position = ego_state.position
                    obs_position = obs_state.position

                    distance = ((ego_position[0] - obs_position[0])**2 + (ego_position[1] - obs_position[1])**2)**(1/2)
                    
                    try:
                        ego_vel_x = ego_state.velocity
                        ego_vel_y = ego_state.velocity_y
                    except:
                        ego_vel_x = (ego_state.velocity)*sin(ego_state.orientation)
                        ego_vel_y = (ego_state.velocity)*cos(ego_state.orientation)

                    try:
                        obs_vel_x = obs_state.velocity
                        obs_vel_y = obs_state.velocity_y
                    except:
                        obs_vel_x = (obs_state.velocity)*sin(obs_state.orientation)
                        obs_vel_y = (obs_state.velocity)*cos(obs_state.orientation)

                    relative_speed_x = ego_vel_x - obs_vel_x
                    relative_speed_y = ego_vel_y - obs_vel_y

                    relative_speed = ((relative_speed_x)**2 + (relative_speed_y)**2)**(1/2)


                    if ego_position[0] < obs_position[0] and ego_position[1] < obs_position[1]:
                        if relative_speed_x < 0 or relative_speed_y < 0:
                            relative_speed = - relative_speed
                        else:
                            pass
                    elif ego_position[0] > obs_position[0] and ego_position[1] > obs_position[1]:
                        if relative_speed_x > 0 or relative_speed_y > 0:
                            relative_speed = - relative_speed
                        else:
                            pass
                    elif ego_position[0] == obs_position[0]:
                        if relative_speed_x < 0:
                            relative_speed = - relative_speed
                        else:
                            pass
                    elif ego_position[1] == obs_position[1]:
                        if relative_speed_y < 0:
                            relative_speed = - relative_speed
                        else:
                            pass

                    try:
                        phase = (ego_state.orientation - obs_state.orientation)*(pi/2)
                    except:
                        phase = (atan2(obs_position[1] - ego_position[1], obs_position[0] - ego_position[0]))*(pi/2)

                    if relative_speed < 0:
                        phase = - phase
                    
                    mdtc = 0.3443*sin(phase) - 0.005811*sin(2*phase) - 0.06834*sin(3*phase) 
                    + 0.01177*sin(4*phase) + 0.04933*sin(5*phase)- 0.01347*sin(6*phase) - 0.002292*sin(7*phase) 
                    + 0.01041*sin(8*phase) + 0.01556*sin(9*phase) - 0.008126*sin(10*phase) - 0.0009892*sin(11*phase) 
                    + 0.007698*sin(12*phase) + 0.001044*sin(13*phase) - 0.005202*sin(14*phase) + 0.01056*sin(15*phase) 
                    + 0.001526*sin(16*phase) - 0.01129*sin(17*phase)

                    partial_cost = 23.22 * (distance**(-1)) * relative_speed * mdtc

                if partial_cost <= 0:
                    pass
                else:
                    total_cost += partial_cost
                    
        return total_cost
    except Exception as ex:
        msg = f"An exception occurred during calculation of VCRO cost!"
        raise PartialCostFunctionException(msg) from ex


def r(
    scenario: Scenario, planning_problem: PlanningProblem, trajectory: Trajectory,
        properties: Dict[SolutionProperties, Dict[int,Any]]
) -> float:
    
    """
    Calculates the Rules cost.
    """
    try:

        total_cost = 0
        scenario_aux = copy.deepcopy(scenario)
        
        ego_shape = Rectangle(length=1, width=1)
        ego_prediction = TrajectoryPrediction(trajectory=trajectory,shape=ego_shape)
        ego_id = scenario_aux.generate_object_id()
        ego_type = ObstacleType.UNKNOWN
        ego = DynamicObstacle(obstacle_id=ego_id, obstacle_type=ego_type,
                                    obstacle_shape=ego_shape, initial_state=trajectory.state_list[0],
                                    prediction=ego_prediction)
        scenario_aux.add_objects(ego)

        cr_eval = CommonOceanObstacleEvaluation(config_path=os.path.dirname(rules.__file__) + '/')
        result = cr_eval.evaluate_scenario(scenario_aux, flag_print = False)
        for elem in result:
            if elem[0] == ego_id:
                dic_result = elem[1]
                if all(rule for rule in dic_result.values()):
                    total_cost = 0
                else:
                    total_cost = 1
            else:
                pass
        
        return total_cost

    except Exception as ex:
        msg = f"An exception occurred during calculation of Rules (R) cost!"
        raise PartialCostFunctionException(msg) from ex
