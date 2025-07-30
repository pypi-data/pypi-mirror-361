from collections import defaultdict
from copy import deepcopy
from enum import Enum
from functools import lru_cache
from typing import Union, Any, Optional

import shapely
import shapely.geometry
from commonocean.common.solution import VesselType
from commonocean.scenario.scenario import Scenario

from commonroad.common.util import Interval, subtract_orientations

from commonocean.scenario.trajectory import Trajectory
from commonocean.scenario.state import State
from commonocean_dc.collision.collision_detection.scenario import create_collision_checker_scenario

from commonroad_dc import pycrcc
from commonocean_dc.collision.collision_detection.pycrcc_collision_dispatch import create_collision_object
from commonocean_dc.feasibility.vessel_dynamics import VesselParameterMapping
from commonocean_dc.geometry.util import chaikins_corner_cutting, resample_polyline
from commonroad_dc.pycrcc import CollisionObject, CollisionChecker, Circle

from typing import List, Dict, Tuple
import numpy as np
import matplotlib.pyplot as plt

from commonocean.scenario.waters import WatersNetwork

from commonroad_dc.pycrccosy import CurvilinearCoordinateSystem
from shapely.geometry import Polygon

draw_waters_path = True
use_shapely = True

def merge_trajectories(traj_1: Trajectory, traj_2: Trajectory):
    traj = deepcopy(traj_1)
    for s, s2 in zip(traj.state_list, traj_2.state_list):
        for attr in s.__slots__:
            if not hasattr(s, attr) and hasattr(s2, attr):
                setattr(s, attr, getattr(s2, attr))

    return traj


def smoothen_polyline(polyline, resampling_distance: float = 2.0, n_lengthen=3):
    for _ in range(3):
        polyline = np.array(chaikins_corner_cutting(polyline))

    resampled_polyline = resample_polyline(polyline, resampling_distance)

    # lengthen by n_lengthen points
    for _ in range(n_lengthen):
        resampled_polyline = np.insert(resampled_polyline, 0,
                                       2 * resampled_polyline[0] - resampled_polyline[1], axis=0)
        resampled_polyline = np.insert(resampled_polyline, len(resampled_polyline),
                                       2 * resampled_polyline[-1] - resampled_polyline[-2], axis=0)

    return resampled_polyline


def extrapolate_polyline(polyline: np.ndarray, offset: float = 10) -> np.ndarray:
    """
    Current ccosy creates wrong projection domain if polyline has large distance between waypoints --> resampling;
    initial and final points are not within projection domain -> extrapolation
    :param polyline: polyline to be used to create ccosy
    :param offset: offset of newly created vertices
    :return: extrapolated polyline
    """
    d1 = (polyline[0] - polyline[1]) / np.linalg.norm(polyline[0] - polyline[1])
    d2 = (polyline[-1] - polyline[-2]) / np.linalg.norm(polyline[-1] - polyline[-2])
    first = polyline[0] + d1 * offset
    first = first[np.newaxis]
    last = polyline[-1] + d2 * offset
    last = last[np.newaxis]

    return np.concatenate((first, polyline, last), axis=0)


def create_cosy_from_waters(waters):
    v0 = waters.center_vertices
    v = smoothen_polyline(extrapolate_polyline(v0), resampling_distance=2.5, n_lengthen=0)
    tt = CurvilinearCoordinateSystem(v)
    return tt
    # raise ValueError

    dom = np.array(tt.projection_domain())
    plt.fill(dom[:,0], dom[:,1], fill=False)
    domc = np.array(tt.curvilinear_projection_domain())
    for ii, d in enumerate(dom):
        try:
            tt.convert_to_curvilinear_coords(d[0], d[1])
            plt.scatter(d[0], d[1], marker='x', c='r')
        except ValueError:
            plt.scatter(d[0], d[1], marker='x', c='g')

    poly = Polygon(dom)
    poly = poly.buffer(-.5)
    plt.plot(np.array(poly.exterior.coords)[:,0], np.array(poly.exterior.coords)[:,1])
    for ii, d in enumerate(np.array(poly.exterior.coords)):
        try:
            tt.convert_to_curvilinear_coords(d[0], d[1])
            plt.scatter(d[0], d[1], marker='x', c='r')
        except ValueError:
            plt.scatter(d[0], d[1], marker='x', c='g')

    plt.show(block=True)
    # print(tt)
    return tt
        # return CurvilinearCoordinateSystem(waters.center_vertices)

    # except RuntimeError:
    #     return None


def create_cosy_from_vertices(center_vertices):
    try:
        return CurvilinearCoordinateSystem(smoothen_polyline(extrapolate_polyline(center_vertices, 2.0)))
    except RuntimeError:
        return None


def get_orientation_at_position(cosy, position):
    try:
        s, d = cosy.convert_to_curvilinear_coords(position[0], position[1])
        tangent = cosy.tangent(s)
    except ValueError as e:
        # print(str(e))
        return None

    return np.arctan2(tangent[1], tangent[0])


def cleanup_discontinuities(positions: np.ndarray, ds_0: float, tol: float, dt: float):
    """
    remove discontinuities from a signal.
    :param signal: signal to be checked
    :param ds0: initial first order derivative of signal
    :param tol: max. absolute deviation between signal states at subsequent time steps
    :param dt: time step
    :return:
    """
    ds = ds_0
    ds2_0 = 0.0
    dt2 = 0.5 * dt ** 2
    positions_new = deepcopy(positions)
    delta_s = 0
    for i, (s_prev, s) in enumerate(zip(positions[:-1], positions[1:])):
        s_pred_new = positions_new[i] + ds * dt + ds2_0 * dt2
        s_pred     = s_prev           + ds * dt + ds2_0 * dt2
        # replace with prediction if unreasonable discontinuity
        if abs(s - s_pred) > tol:
            positions_new[i+1] = s_pred_new
            delta_s += s_pred - s
        else:
            positions_new[i + 1] = s + delta_s
            ds_prev = ds
            ds = (s - s_prev) / dt
            if i > 0:
                dt2 = (ds - ds_prev) / dt

    return positions_new


class SolutionProperties(Enum):
    AllowedVelocityInterval = "ALLOWED_VELOCITY_INTERVAL"
    LongPosition = "LONG_POSITION"
    LatPosition = "LAT_POSITION"
    LonJerk = "LON_JERK"
    LonVelocity = "LAT_VELOCITY"
    LatJerk = "LAT_JERK"
    LatVelocity = "LAT_VELOCITY"
    LonDistanceObstacles = "LON_DISTANCE_OBSTACLES"
    DeltaOrientation = "DELTA_ORIENTATION"

class WatersRouteMatcher:
    """
    Finds waters paths of vessels' trajectories and transforms to lane-based coordinate systems.
    """
    def __init__(self, scenario: Scenario, vessel_type: VesselType):
        param = VesselParameterMapping.from_vessel_type(vessel_type)
        self.ego_radius = param.w / 2.5
        self.scenario: Scenario = scenario
        self.waters_network: WatersNetwork = scenario._waters_network
        self.waters_cc: Union[CollisionChecker, Dict[int, shapely.geometry.Polygon]] = CollisionChecker()
        self.co2waters: Dict[CollisionObject, int] = {}
        self.waters_cc, self.co2waters = self._create_cc_from_waters_network(self.waters_network)
        self._waters_cosys = {}

    @lru_cache(1)
    def scenario_cc(self):
        return create_collision_checker_scenario(self.scenario)

    @staticmethod
    def _create_cc_from_waters_network(ln: WatersNetwork) -> Tuple[CollisionChecker, Dict[CollisionObject, int]]:
        """Creates Collision Checker"""
        if use_shapely is True:
            cc = {}
        else:
            cc = CollisionChecker()
        co2waters: Dict[CollisionObject, int] = {}
        for l in ln.waterways:
            poly = l.convert_to_polygon()
            # assert poly.shapely_object.is_valid
            if use_shapely is True:
                cc[l.waters_id] = poly.shapely_object
            else:
                co: pycrcc.Polygon = create_collision_object(poly)
                co2waters[co] = l.waters_id
                cc.add_collision_object(co)

        return cc, co2waters

    def find_waters_by_position(self, position: np.ndarray) -> List[int]:
        if use_shapely is True:
            point = shapely.geometry.Point(position).buffer(self.ego_radius, resolution=8)
            return [id_l for id_l, shape in self.waters_cc.items() if shape.intersects(point)]
        else:
            cc_obs = self.waters_cc.find_all_colliding_objects(Circle(self.ego_radius, position[0], position[1]))
            return [self.co2waters[o] for o in cc_obs]

    def get_waters_cosy(self, waters_id: int) -> CurvilinearCoordinateSystem:
        if waters_id not in self._waters_cosys:
            self._waters_cosys[waters_id] = create_cosy_from_waters(
                self.waters_network.find_waters_by_id(waters_id))

        return self._waters_cosys[waters_id]

    def _select_by_best_alignment(self, waters2states: Dict[int, List[State]],
                                  successor_candidates: List[List[int]]) -> Optional[List[int]]:
        """
        Computes mean square error of deviation of orientations compared to waters in successor_candidates
        :param obstacle
        :param successor_candidates_tmp:
        :return: list with ids (only those which have a feasible projection/tangent) ranked by deviation (best first)
        """
        if len(successor_candidates)==1:
            return successor_candidates[0]

        # compute tangential vectors of trajectory
        errors = {}
        # print(successor_candidates)
        for i, waters in enumerate(successor_candidates):
            errors_tmp = []

            v = np.concatenate(
                [self.waters_network.find_waters_by_id(l).center_vertices for l in waters if l is not None])
            cosy = create_cosy_from_vertices(v)
            if cosy is None:
                continue
            for l in waters:
                for s in waters2states[l]:
                    ori = get_orientation_at_position(cosy, s.position)
                    if ori is not None:
                        errors_tmp.append(subtract_orientations(s.orientation, ori))

            # compute mean square error for deviation of tangent (only if tangent was feasible)
            if len(errors_tmp) > 0:
                errors[i] = np.square(errors_tmp).mean(axis=0)
        
        try:
            best_index = sorted(errors.keys(), key=errors.get)[0]
        except IndexError:
            return None
        return successor_candidates[best_index]

    def find_waters_by_trajectory(self, trajectory: Trajectory, required_properties: List[SolutionProperties],
                                    exclude_oncoming_lanes=True) \
            -> Tuple[List[int], Dict[SolutionProperties, Dict[int, Any]]]:
        properties = {}

        if len(trajectory.state_list) < 1:
            return [], None

        max_dist = max(s.velocity for s in trajectory.state_list) * self.scenario.dt  # per time_step

        assert hasattr(trajectory.state_list[0], "position"), "Trajectory must have slot 'position'!"
        # find all waters at each time step
        waters = []
        waters2states = defaultdict(list)
        for state in trajectory.state_list:
            waters.append(self.find_waters_by_position(state.position))
            for l in waters[-1]:
                waters2states[l].append(state)

        # find sequence of waters considering adjacencies
        l_seq = []
        candidate_paths_next = []

        for i, l_tmp in enumerate(waters):
            candidate_paths = candidate_paths_next
            candidate_paths_next = []
            if not candidate_paths and l_seq:
                candidate_paths = [[l_seq[-1]]]

            if len(l_tmp) > 0:
                if candidate_paths:
                    # check for longitudinal adjacency
                    for c_path in candidate_paths:
                        if set(c_path) & set(l_tmp):
                            candidate_paths_next.append(c_path)
                            continue

                        # find successor paths that lead to one current waters of t_tmp
                        # (considers that short waters can be skipped)
                        waters_prev = self.waters_network.find_waters_by_id(c_path[-1])
                        successor_paths = waters_prev.find_waters_successors_in_range(self.waters_network,
                                                                                        max_length=max_dist)
                        in_successor_list = []
                        for succ_p in successor_paths:
                            if set(l_tmp) & set(succ_p):
                                succ_path = []
                                for s_tmp in succ_p:
                                    succ_path.append(s_tmp)
                                    if s_tmp in l_tmp:
                                        break
                                in_successor_list.append(succ_path)

                        if in_successor_list:
                            # create new candidates
                            candidate_paths_next.extend([c_path + l for l in in_successor_list])
                        else:
                            # check for lateral adjacency
                            adj = set()
                            if waters_prev.adj_left and waters_prev.adj_left_same_direction:
                                adj.add(waters_prev.adj_left)
                            if waters_prev.adj_right and waters_prev.adj_right_same_direction:
                                adj.add(waters_prev.adj_right)

                            adj_list = adj & set(l_tmp)
                            if adj_list:
                                candidate_paths_next.extend([c_path + [l] for l in adj_list])
                                continue

                else:
                    # first state -> no adjacency checks possible
                    candidate_paths_next = [[None, l] for l in l_tmp]

                if len(candidate_paths_next) == 0:
                    # leaves route (e.g. drives to diagonal successor or conducts U-turn to oncoming lane)
                    # 1. check if still in projection domain of previous cosy or successor
                    for c_path in candidate_paths:
                        if set(c_path) & set(l_tmp):
                            continue
                        if self.get_waters_cosy(c_path[-1]). \
                                cartesian_point_inside_projection_domain(trajectory.state_list[i].position[0],
                                                                         trajectory.state_list[i].position[1]):
                            candidate_paths_next.append(c_path)
                        else:
                            # select successor path with best alignment
                            waters_tmp = self.waters_network.find_waters_by_id(c_path[-1])
                            if i > 0:
                                dist = 10
                            else:
                                dist = 10 + np.linalg.norm([trajectory.state_list[i].position,
                                                            trajectory.state_list[i-1].position],
                                                           ord=np.inf)

                            successors = waters_tmp.find_waters_successors_in_range(self.waters_network, dist)
                            succ_candidates = []
                            for path in successors:
                                select_path = False
                                for i_l, l_id_tmp in enumerate(path):
                                    if self.get_waters_cosy(l_id_tmp). \
                                            cartesian_point_inside_projection_domain(
                                            trajectory.state_list[i].position[0],
                                            trajectory.state_list[i].position[1]):
                                        select_path = True
                                    else:
                                        break

                                if select_path:
                                    succ_candidates.append(c_path + path[:i_l+1])

                            if len(succ_candidates) > 0:
                                best_path = self._select_by_best_alignment(waters2states, succ_candidates)
                                if best_path:
                                    candidate_paths_next.append(best_path[1:])

                    if len(candidate_paths_next) == 0:
                        # still no candidate -> add by best alignement
                        if candidate_paths:
                            best_path = self._select_by_best_alignment(waters2states, candidate_paths)
                            if best_path:
                                l_seq.extend(best_path[1:])
                                candidate_paths_next = [[None, l] for l in l_tmp]

                if len(candidate_paths_next) == 1:
                    # only one candidate path left -> add to sequence and reset
                    l_seq.extend(candidate_paths_next[0][1:])
                    candidate_paths_next = []

            else:
                continue

            if SolutionProperties.AllowedVelocityInterval in required_properties:

                speed_intervals = {}
                
                for i, l_list_tmp in enumerate(waters):
                    # l_tmp = frozenset(l_list_tmp) & frozenset(l_seq)
                    # if not l_list_tmp:
                    #     l_tmp = frozenset(l_list_tmp)

                    # min_speed = tsi.required_speed(l_tmp)
                    # min_speed = 0.0 if min_speed is None else min_speed
                    # max_speed = tsi.speed_limit(l_tmp)
                    # max_speed = np.inf if max_speed is None else max_speed
                    # speed_intervals[i] = Interval(min_speed, max_speed)
                    speed_intervals[i] = Interval(0.0, np.inf)

                properties[SolutionProperties.AllowedVelocityInterval] = speed_intervals

        # check if there are candidates left and use best aligned candidate
        if candidate_paths_next:
            best_path = self._select_by_best_alignment(waters2states, candidate_paths_next)
            if best_path:
                l_seq.extend(best_path[1:])

        if exclude_oncoming_lanes and len(l_seq) > 1:
            # exclude oncoming lanes when switching back to previous lane
            onc_tmp = None
            delete_i = []
            waters_prev = self.waters_network.find_waters_by_id(l_seq[0])
            for i, l in enumerate(l_seq[1:]):
                if onc_tmp is not None:
                    if l in l_seq[:i]:
                        delete_i.append(i)
                    else:
                        onc_tmp = None

                lanlet = self.waters_network.find_waters_by_id(l)
                oncomings = []
                if waters_prev.adj_left and not waters_prev.adj_left_same_direction:
                    oncomings.append(waters_prev.adj_left)
                if waters_prev.adj_right and not waters_prev.adj_right_same_direction:
                    oncomings.append(waters_prev.adj_right)

                if l in oncomings:
                    onc_tmp = l
                else:
                    onc_tmp = None

                waters_prev = lanlet

            # for i_del in reversed(delete_i):
            #     del l_seq[i_del]

        return l_seq, properties

    def calculate_properties(self, trajectory: Trajectory, required_properties: List[SolutionProperties]) \
            -> Dict[SolutionProperties, Dict[int, Any]]:
        """
        Calculates necessary properties for the partial costs
        :param trajectory: trajectory in cartesian coordinates
        :param required_properties: additional properties that should be retrieved
        :return:
        """
        properties = {}

        if SolutionProperties.LonDistanceObstacles in required_properties:
            properties[SolutionProperties.LonDistanceObstacles] = {}
            obstacles = self.scenario.dynamic_obstacles

            for state in trajectory.state_list:
                ego_pos = state.position
                dist_lon = []
                for vessel in obstacles:
                    position_obs = vessel.state_at_time(state.time_step).position

                    dist = ((ego_pos[0] - position_obs[0])**2 + (ego_pos[1]-position_obs[1])**2)**(1/2)

                    if dist < 2.8 and dist > 0:
                        dist_lon.append(dist - self.ego_radius)
                    else:
                        dist_lon.append(dist)

                properties[SolutionProperties.LonDistanceObstacles][state.time_step] = max(dist_lon)

        if SolutionProperties.LatJerk in required_properties:
            properties[SolutionProperties.LatJerk] = {}
            for state in trajectory.state_list:
                    properties[SolutionProperties.LatJerk][state.time_step] = 0.0

        if SolutionProperties.LonJerk in required_properties:
            properties[SolutionProperties.LonJerk] = {}
            for state in trajectory.state_list:
                    properties[SolutionProperties.LonJerk][state.time_step] = 0.0

        if SolutionProperties.LonVelocity in required_properties:
            properties[SolutionProperties.LonVelocity] = {}
            for state in trajectory.state_list:
                    properties[SolutionProperties.LonVelocity][state.time_step] = 0.0

        if SolutionProperties.AllowedVelocityInterval in required_properties:
            properties[SolutionProperties.AllowedVelocityInterval] = {}
            for state in trajectory.state_list:
                    properties[SolutionProperties.AllowedVelocityInterval][state.time_step] = 0.0

        return properties
