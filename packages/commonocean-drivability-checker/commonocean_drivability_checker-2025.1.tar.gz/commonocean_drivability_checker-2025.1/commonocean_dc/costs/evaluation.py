import itertools
from enum import Enum
from typing import Dict, List, Tuple

from commonocean.planning.planning_problem import PlanningProblem, PlanningProblemSet
from commonocean.scenario.scenario import Scenario
from commonocean.scenario.trajectory import Trajectory
from commonocean_dc.costs.route_matcher import WatersRouteMatcher, SolutionProperties

from commonocean.common.solution import Solution, CostFunction, VesselType

import commonocean_dc.costs.partial_cost_functions as cost_functions

class PartialCostFunction(Enum):
    """
    See our cost functions for more details.

    A: Acceleration,
    J: Jerk,
    Jlat: Lateral Jerk,
    Jlon: Longitudinal Jerk,
    RA: Rudder Angle,
    RR: Rudder Rate,
    Y: Yaw Rate,
    V: Velocity Offset,
    Vlon: Longitudinal Velocity Offset,
    O: Orientation Offset,
    D: Distance to Obstacles,
    T: Time,
    ID: Inverse Duration,
    R: Rule compliance
    """

    A = "A"
    J = "J"
    Jlat = "Jlat"
    Jlon = "Jlon"
    RA = "RA"
    RR = "RR"
    Y = "Y"
    V = "V"
    Vlon = "Vlon"
    O = "O"
    D = "D"
    T = "T"
    ID = "ID"
    VCRO = "VCRO"
    R = "R"


PartialCostFunctionMapping = {
    PartialCostFunction.A:  cost_functions.acceleration_cost,
    PartialCostFunction.J:  cost_functions.jerk_cost,
    PartialCostFunction.Jlat:  cost_functions.jerk_lat_cost,
    PartialCostFunction.Jlon:  cost_functions.jerk_lon_cost,
    PartialCostFunction.RA:  cost_functions.rudder_angle_cost,
    PartialCostFunction.RR:  cost_functions.rudder_rate_cost,
    PartialCostFunction.Y:  cost_functions.yaw_cost,
    PartialCostFunction.V:  cost_functions.velocity_offset_cost,
    PartialCostFunction.Vlon:  cost_functions.longitudinal_velocity_offset_cost,
    PartialCostFunction.O:  cost_functions.orientation_offset_cost,
    PartialCostFunction.D:  cost_functions.distance_to_obstacle_cost,
    PartialCostFunction.T:  cost_functions.time_cost,
    PartialCostFunction.ID:  cost_functions.inverse_duration_cost,
    PartialCostFunction.VCRO: cost_functions.vcro,
    PartialCostFunction.R: cost_functions.r
}

cost_function_mapping =\
    {
        CostFunction.JB1: [
            (PartialCostFunction.T, 1.0)
        ],

        CostFunction.VRCO1: [
            (PartialCostFunction.VCRO, 1.0)
        ],

        CostFunction.RC1: [
            (PartialCostFunction.R, 1.0)
        ],

        CostFunction.SB1: [
            (PartialCostFunction.T, 0.1),
            (PartialCostFunction.A, 0.5),
            (PartialCostFunction.R, 200)
        ]
    }

# additional attributes that need to be computed before evaluation
required_properties = {
    PartialCostFunction.A: [],
    PartialCostFunction.J: [],
    PartialCostFunction.Jlat: [SolutionProperties.LatJerk],
    PartialCostFunction.Jlon: [SolutionProperties.LonJerk],
    PartialCostFunction.RA: [],
    PartialCostFunction.RR: [],
    PartialCostFunction.Y: [],
    PartialCostFunction.V: [],
    PartialCostFunction.Vlon: [SolutionProperties.LonVelocity, SolutionProperties.AllowedVelocityInterval],
    PartialCostFunction.O: [],
    PartialCostFunction.D: [SolutionProperties.LonDistanceObstacles],
    PartialCostFunction.T: [],
    PartialCostFunction.ID: [], 
    PartialCostFunction.VCRO: [],
    PartialCostFunction.R: []}


class CostFunctionEvaluator:
    def __init__(self, cost_function_id: CostFunction, vessel_type: VesselType):
        self.cost_function_id: CostFunction = cost_function_id
        self.vessel_type = vessel_type
        self.partial_cost_funcs: List[Tuple[PartialCostFunction,float]] = cost_function_mapping[self.cost_function_id]

    @classmethod
    def init_from_solution(cls, solution: Solution):
        return cls(cost_function_id=CostFunction[solution.cost_ids[0]],
                   vessel_type=VesselType(int(solution.vessels_ids[0][-1])))

    @property
    def required_properties(self):
        return list(itertools.chain.from_iterable(required_properties[p] for p, _ in self.partial_cost_funcs))

    def evaluate_pp_solution(self, cr_scenario: Scenario, cr_pproblem: PlanningProblem, trajectory: Trajectory,
            draw_waters_path=False, debug_plot=False):
        """
        Computes costs of one solution for cr_pproblem.

        :param cr_scenario: scenario
        :param cr_pproblem: planning problem that is solved by trajectory
        :param trajectory: solution trajectory
        :param draw_waters_path: optionally visualize the detected waters path with respect to whose some parameters for the cost computation are determined (only useful for development).
        :param debug_plot: show plot in case a trajectory cannot be transformed to curvilinear coordinates.
        :return: result of evaluation
        """
        evaluation_result = PlanningProblemCostResult(cost_function_id=self.cost_function_id,
                                                      solution_id=cr_pproblem.planning_problem_id)
        lm = WatersRouteMatcher(cr_scenario, self.vessel_type)
        properties = lm.calculate_properties(trajectory,required_properties=self.required_properties)
        
        for pcf, weight in self.partial_cost_funcs:
            pcf_func = PartialCostFunctionMapping[pcf]
            evaluation_result.add_partial_costs(pcf, pcf_func(cr_scenario, cr_pproblem, trajectory, properties), weight)

        return evaluation_result

    def evaluate_solution(self, scenario: Scenario, cr_pproblems: PlanningProblemSet, solution: Solution)\
            -> "SolutionResult":
        """
        Computes costs for all solutions of a planning problem set.

        :param scenario: scenario that was solved
        :param cr_pproblems: planning problem set that was solved
        :param solution: Solution object that contains trajectories
        :return: SolutionResult object that contains partial and total costs
        """
        results = SolutionResult(benchmark_id=solution.benchmark_id)
        for pps in solution.planning_problem_solutions:
            results.add_results(
                    self.evaluate_pp_solution(scenario, cr_pproblems.planning_problem_dict[pps.planning_problem_id],
                                              pps.trajectory, False))

        return results


class PlanningProblemCostResult:
    def __init__(self, cost_function_id: CostFunction, solution_id: int):
        """
        Contains results of a single solution of a planning problem.

        """
        self.cost_function_id = cost_function_id
        self.partial_costs: Dict[PartialCostFunction, float] = {}
        self.weights: Dict[PartialCostFunction, float] = {}
        self.solution_id: int = solution_id

    @property
    def total_costs(self) -> float:
        c = 0.0
        for pcf, cost in self.partial_costs.items():
            c += cost * self.weights[pcf]

        return c

    def add_partial_costs(self, pcf: PartialCostFunction, cost: float, weight):
        self.partial_costs[pcf] = cost
        self.weights[pcf] = weight

    def __str__(self):
        nl = "\n"
        t = "\t"
        return f"Partial costs for solution of planning problem {self.solution_id}:\n" \
               f"{nl.join([p.name + ':' + t + str(self.weights[p] * c) for p, c in self.partial_costs.items()])}"


class SolutionResult:
    def __init__(self, benchmark_id: str, pp_results: List[PlanningProblemCostResult] = ()):
        """
        Contains results of all solutions of a planning problem set.

        """
        self.benchmark_id: str = benchmark_id
        self.total_costs: float = 0.0
        self.pp_results: Dict[int, PlanningProblemCostResult] = {}
        for r in pp_results:
            self.add_results(r)

    def add_results(self, pp_result: PlanningProblemCostResult):
        self.pp_results[pp_result.solution_id] = pp_result
        self.total_costs += pp_result.total_costs

    def __str__(self):
        nl = "\n\t"
        return f"Total costs for benchmark {self.benchmark_id}:\n" \
               f"{self.total_costs}\n" \
               f"{nl.join(str(pr) for pr in self.pp_results.values())}"
