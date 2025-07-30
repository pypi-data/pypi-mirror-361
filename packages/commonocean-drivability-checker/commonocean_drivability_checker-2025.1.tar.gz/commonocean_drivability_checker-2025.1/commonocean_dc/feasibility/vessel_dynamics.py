from abc import ABC, abstractmethod
from enum import Enum, unique
from typing import List, Union, Tuple

import numpy as np
import math
from commonocean.common.solution import VesselType, VesselModel
from commonroad.geometry.shape import Rectangle
from commonocean.scenario.trajectory import Trajectory
from commonocean.scenario.state import PMState, YPState, TFState, PMInputState, YPInputState, TFInputState

from scipy.integrate import odeint
from scipy.optimize import Bounds

from vesselmodels.parameters_vessel_1 import parameters_vessel_1
from vesselmodels.parameters_vessel_2 import parameters_vessel_2
from vesselmodels.parameters_vessel_3 import parameters_vessel_3
from vesselmodels.vessel_dynamics_pm import vessel_dynamics_pm
from vesselmodels.vessel_dynamics_vp import vessel_dynamics_vp
from vesselmodels.vessel_dynamics_yp import vessel_dynamics_yp
from vesselmodels.vessel_dynamics_3F import vessel_dynamics_3f
from vesselmodels.vessel_parameters import VesselParameters

from vesselmodels.utils.input_constraints import velocity_constraints

class VesselDynamicsException(Exception):
    pass


class FrictionCircleException(VesselDynamicsException):
    pass


class InputBoundsException(VesselDynamicsException):
    pass


class StateException(VesselDynamicsException):
    pass


class InputException(VesselDynamicsException):
    pass


@unique
class VesselParameterMapping(Enum):
    """
    Mapping for VesselType name to VesselParameters
    """
    Vessel1 = parameters_vessel_1()
    Vessel2 = parameters_vessel_2()
    Vessel3 = parameters_vessel_3()

    @classmethod
    def from_vessel_type(cls, vessel_type: VesselType) -> VesselParameters:
        return cls[vessel_type.name].value


class VesselDynamics(ABC):
    """
    VesselDynamics abstract class that encapsulates the common methods of all VesselDynamics classes.

    List of currently implemented vessel models
     - Point Mass Model (PM)
     - Velocity-Constrained Point Mass (VP)
     - Yaw-Constrained Model (YP)
     - Three Degrees of Freedom Model (TF)

    New types of VesselDynamics can be defined by extending this class. If there isn't any mismatch with the state
    values, the new VesselDynamics class can be used directly with the feasibility checkers as well.

    For detailed documentation of the Vessel Models, please check our `Vessel Model Documentation
    <https://commonocean.cps.cit.tum.de/commonocean-models>`_
    """

    def __init__(self, vessel_model: VesselModel, vessel_type: VesselType):
        """
        Creates a VesselDynamics model for the given VesselType.

        :param vessel_type: VesselType
        """
        self.vessel_model = vessel_model
        self.vessel_type = vessel_type
        self.parameters = VesselParameterMapping[self.vessel_type.name].value
        self.shape = Rectangle(length=self.parameters.l, width=self.parameters.w)

    @classmethod
    def PM(cls, vessel_type: VesselType) -> 'PointMassDynamics':
        """
        Creates a PointMassDynamics model.

        :param vessel_type: VesselType, i.e. VesselType.Vessel1
        :return: PointMassDynamics instance with the given vessel type.
        """
        return PointMassDynamics(vessel_type)
    
    @classmethod
    def VP(cls, vessel_type: VesselType) -> 'VelocityConstrainedPointMass':
        """
        Creates a VelocityConstrainedPointMass model.

        :param vessel_type: VesselType, i.e. VesselType.Vessel1
        :return: VelocityConstrainedPointMass instance with the given vessel type.
        """
        return VelocityConstrainedPointMass(vessel_type)

    @classmethod
    def YP(cls, vessel_type: VesselType) -> 'YawConstrained':
        """
        Creates a YawConstrained model.

        :param vessel_type: VesselType, i.e. VesselType.Vessel1
        :return: YawConstrained instance with the given vessel type.
        """
        return YawConstrained(vessel_type)

    @classmethod
    def TF(cls, vessel_type: VesselType) -> 'ThreeDegreesOfFreedom':
        """
        Creates a ThreeDegreesOfFreedom VesselDynamics model.

        :param vessel_type: VesselType, i.e. VesselType.Vessel1
        :return: ThreeDegreesOfFreedom instance with the given vessel type.
        """
        return ThreeDegreesOfFreedom(vessel_type)

    @classmethod
    def from_model(cls, vessel_model: VesselModel, vessel_type: VesselType) -> 'VesselDynamics':
        """
        Creates a VesselDynamics model for the given vessel model and type.

        :param vessel_model: VesselModel, i.e. VesselModel.YP
        :param vessel_type: VesselType, i.e. VesselType.Vessel1
        :return: VesselDynamics instance with the given vessel type.
        """
        model_constructor = getattr(cls, vessel_model.name)
        return model_constructor(vessel_type)

    @abstractmethod
    def dynamics(self, t, x, u) -> List[float]:
        """
        Vessel dynamics function that models the motion of the vessel during forward simulation.

        :param t: time point which the differentiation is being calculated at.
        :param x: state values
        :param u: input values
        :return: next state values
        """
        pass

    @property
    def input_bounds(self) -> Bounds:
        """
        Returns the bounds on inputs (constraints).

        Bounds are
            - min steering velocity <= steering_angle_speed <= max steering velocity
            - -max longitudinal acc <= acceleration <= max longitudinal acc

        :return: Bounds
        """
        # temporary solution as CO does not have constraints as defined in CR
        if self.vessel_model == VesselModel.TF:
            return Bounds([-np.inf, -np.inf, -np.inf],
                        [np.inf, np.inf, np.inf])
        else:
            return Bounds([-np.inf, -np.inf],
                        [np.inf, np.inf])

    def input_within_bounds(self, u: Union[PMInputState, YPInputState, TFInputState, np.array], throw: bool = False) -> bool:
        """
        Checks whether the given input is within input constraints of the vessel dynamics model.

        :param u: input values as np.array or State - Contains 2 values
        :param throw: if set to false, will return bool instead of throwing exception (default=False)
        :return: True if within constraints
        """
        return True # temporary solution as CO does not have constraints as defined in CR

        # inputs = self.input_to_array(u)[0] if isinstance(u, State) else u
        # in_bounds = all([self.input_bounds.lb[idx] <= round(inputs[idx], 4) <= self.input_bounds.ub[idx]
        #                  for idx in range(len(self.input_bounds.lb))])
        # if not in_bounds and throw:
        #     raise InputBoundsException(f'Input is not within bounds!\nInput: {u}')
        # return in_bounds


    def forward_simulation(self, x: np.array, u: np.array, dt: float, throw: bool = True) -> Union[None, np.array]:
        """
        Simulates the next state using the given state and input values as numpy arrays.

        :param x: state values.
        :param u: input values
        :param dt: scenario delta time.
        :param throw: if set to false, will return None as next state instead of throwing exception (default=True)
        :return: simulated next state values, raises VesselDynamicsException if invalid input.
        """
        within_bounds = self.input_within_bounds(u, throw)

        x0, x1 = odeint(self.dynamics, x, [0.0, dt], args=(u,), tfirst=True)
        return x1

    def simulate_next_state(self, x: Union[PMState, YPState, TFState], u: Union[PMInputState, YPInputState, TFInputState], dt: float, throw: bool = True) -> Union[None, PMState, YPState, TFState]:
        """
        Simulates the next state using the given state and input values as State objects.

        :param x: current state
        :param u: inputs for simulating the next state
        :param dt: scenario delta time.
        :param throw: if set to false, will return None as next state instead of throwing exception (default=True)
        :return: simulated next state, raises VesselDynamicsException if invalid input.
        """
        x_vals, x_ts = self.state_to_array(x)
        u_vals, u_ts = self.input_to_array(u)
        x1_vals = self.forward_simulation(x_vals, u_vals, dt, throw)
        if x1_vals is None:
            return None
        x1 = self.array_to_state(x1_vals, x_ts + 1)
        return x1

    def simulate_trajectory(self, initial_state: Union[PMState, YPState, TFState], input_vector: Trajectory,
                            dt: float, throw: bool = True) -> Union[None, Trajectory]:
        """
        Creates the trajectory for the given input vector.

        :param initial_state: initial state of the planning problem
        :param input_vector: input vector as Trajectory object
        :param dt: scenario delta time
        :param throw: if set to false, will return None as trajectory instead of throwing exception (default=True)
        :return: simulated trajectory, raises VesselDynamicsException if there is an invalid input.
        """
        converted_init_state = self.convert_initial_state(initial_state)
        state_list = [converted_init_state]
        for input in input_vector.state_list:
            simulated_state = self.simulate_next_state(state_list[-1], input, dt, throw)
            if not throw and not simulated_state:
                return None
            state_list.append(simulated_state)
        trajectory = Trajectory(initial_time_step=initial_state.time_step, state_list=state_list)
        return trajectory

    @abstractmethod
    def _state_to_array(self, state: Union[PMState, YPState, TFState]) -> Tuple[np.array, int]:
        """Actual conversion of state to array happens here, each vessel will implement its own converter."""
        pass

    def state_to_array(self, state: Union[PMState, YPState, TFState]) -> Tuple[np.array, int]:
        """
        Converts the given State to numpy array.

        :param state: GeneralState
        :return: state values as numpy array and time step of the state
        """
        try:
            array, time_step = self._state_to_array(state)
            return array, time_step
        except Exception as e:
            err = f'Not a valid state!\nState:{str(state)}'
            raise StateException(err) from e

    @abstractmethod
    def _array_to_state(self, x: np.array, time_step: int) -> Union[PMState, YPState, TFState]:
        """Actual conversion of the array to state happens here, each vessel will implement its own converter."""
        pass

    def array_to_state(self, x: np.array, time_step: int) -> Union[PMState, YPState, TFState]:
        """
        Converts the given numpy array of values to State.

        :param x: list of state values
        :param time_step: time step of the converted state
        :return: GeneralState
        """
        try:
            state = self._array_to_state(x, time_step)
            return state
        except Exception as e:
            raise e
            # err = f'Not a valid state array!\nTime step: {time_step}, State array:{str(x)}'
            # raise StateException(err) from e

    def convert_initial_state(self, initial_state) -> Union[PMInputState, YPInputState, TFInputState]:
        """
        Converts the given default initial state to VesselModel's state by setting the state values accordingly.

        :param initial_state: default initial state
        :return: converted initial state
        """
        return self.array_to_state(self.state_to_array(initial_state)[0],
                                   initial_state.time_step)

    def _input_to_array(self, input: Union[PMInputState, YPInputState, TFInputState]) -> Tuple[np.array, int]:
        """Actual conversion of input to array happens here, each vessel will implement its own converter."""
        pass

    def input_to_array(self, input: Union[PMInputState, YPInputState, TFInputState]) -> Tuple[np.array, int]:
        """
        Converts the given input (as State object) to numpy array.

        :param input: input as State object
        :return: state values as numpy array and time step of the state, raises VesselDynamicsException if invalid
            input
        """
        try:
            array, time_step = self._input_to_array(input)
            return array, time_step
        except Exception as e:
            raise InputException(f'Not a valid input!\n{str(input)}') from e

    def _array_to_input(self, u: np.array, time_step: int) -> Union[PMInputState, YPInputState, TFInputState]:
        """Actual conversion of input to array happens here, each vessel will implement its own converter."""
        pass
        """
        Actual conversion of input array to input happens here. Vessels can override this method to implement their
        own converter.
        """

        values = {
            'acceleration': u[0],
        }
        return GeneralState(**values, time_step=time_step)

    def array_to_input(self, u: np.array, time_step: int) -> Union[PMInputState, YPInputState, TFInputState]:
        """
        Converts the given numpy array of values to input (as GeneralState object).

        :param u: input values
        :param time_step: time step of the converted input
        :return: input as state object, raises VesselDynamicsException if invalid input
        """
        try:
            state = self._array_to_input(u, time_step)
            return state
        except Exception as e:
            raise InputException(f'Not a valid input array!\nArray:{str(u)} Time Step: {time_step}') from e

    @staticmethod
    def _convert_from_directional_velocity(velocity, orientation) -> Tuple[float, float]:
        """
        Converts the given velocity and orientation to velocity_x and velocity_y values.

        :param velocity: velocity
        :param orientation: orientation
        :return: velocity_x, velocity_y
        """
        velocity_x = np.cos(orientation) * velocity
        velocity_y = np.sin(orientation) * velocity
        return velocity_x, velocity_y

class PointMassDynamics(VesselDynamics):
    def __init__(self, vessel_type: VesselType):
        super(PointMassDynamics, self).__init__(VesselModel.PM, vessel_type)

    def dynamics(self, t, x, u) -> List[float]:
        return vessel_dynamics_pm(x, u, self.parameters)
    
    def _initialize_state(self, raw_state, time_step: int):
        raw_state_parse = {
            "position": [raw_state["position_x"], raw_state["position_y"]],
            "velocity": raw_state["velocity"], 
            "velocity_y": raw_state["velocity_y"],
        }
        return PMState(**raw_state_parse, time_step=time_step)

    def _state_to_array(self, state: PMState) -> Tuple[np.array, int]:
        """ Implementation of the VesselDynamics abstract method. """
        values = [
            state.position[0],
            state.position[1],
            state.velocity,
            state.velocity_y
        ]
        time_step = state.time_step
        return np.array(values), time_step

    def _array_to_state(self, x: np.array, time_step: int) -> PMState:
        """ Implementation of the VesselDynamics abstract method. """
        values = {
            'position': np.array([x[0], x[1]]),
            'velocity': x[2],
            'velocity_y': x[3]
        }
        state = PMState(**values, time_step=time_step)
        return state

    def _input_to_array(self, input: PMInputState) -> Tuple[np.array, int]:
        """ Implementation of the VesselDynamics abstract method. """
        values = [
            input.acceleration,
            input.acceleration_y
        ]
        time_step = input.time_step
        return np.array(values), time_step

    def _array_to_input(self, u: np.array, time_step: int) -> PMInputState:
        """ Implementation of the VesselDynamics abstract method. """
        values = {
            'acceleration': u[0],
            'acceleration_y': u[1]
        }
        return PMInputState(**values, time_step=time_step)

class VelocityConstrainedPointMass(VesselDynamics):
    def __init__(self, vessel_type: VesselType):
        super(VelocityConstrainedPointMass, self).__init__(VesselModel.VP, vessel_type)

    def dynamics(self, t, x, u) -> List[float]:
        return vessel_dynamics_vp(x, u, self.parameters, t)
    
    def _initialize_state(self, raw_state, time_step: int):
        raw_state_parse = {
            "position": [raw_state["position_x"], raw_state["position_y"]],
            "velocity": raw_state["velocity"], 
            "velocity_y": raw_state["velocity_y"],
        }
        return PMState(**raw_state_parse, time_step=time_step)

    def _state_to_array(self, state: PMState) -> Tuple[np.array, int]:
        """ Implementation of the VesselDynamics abstract method. """
        values = [
            state.position[0],
            state.position[1],
            state.velocity,
            state.velocity_y
        ]
        time_step = state.time_step
        return np.array(values), time_step

    def _array_to_state(self, x: np.array, time_step: int) -> PMState:
        """ Implementation of the VesselDynamics abstract method. """
        values = {
            'position': np.array([x[0], x[1]]),
            'velocity': x[2],
            'velocity_y': x[3]
        }
        state = PMState(**values, time_step=time_step)
        return state
    
    def _input_to_array(self, input: PMInputState) -> Tuple[np.array, int]:
        """ Implementation of the VesselDynamics abstract method. """
        values = [
            input.acceleration,
            input.acceleration_y
        ]
        time_step = input.time_step
        return np.array(values), time_step

    def _array_to_input(self, u: np.array, time_step: int) -> PMInputState:
        """ Implementation of the VesselDynamics abstract method. """
        values = {
            'acceleration': u[0],
            'acceleration_y': u[1]
        }
        return PMInputState(**values, time_step=time_step)

class YawConstrained(VesselDynamics):
    def __init__(self, vessel_type: VesselType):
        super(YawConstrained, self).__init__(VesselModel.YP, vessel_type)

    def dynamics(self, t, x, u) -> List[float]:
        return vessel_dynamics_yp(x, u, self.parameters)
    
    def _initialize_state(self, raw_state, time_step: int):
        raw_state_parse = {
            "position": [raw_state["position_x"], raw_state["position_y"]],
            "orientation": raw_state["orientation"], 
            "velocity": raw_state["velocity"],
        }
        return YPState(**raw_state_parse, time_step=time_step)

    def _state_to_array(self, state: YPState) -> Tuple[np.array, int]:
        """ Implementation of the VesselDynamics abstract method. """
        values = [
            state.position[0],
            state.position[1],
            state.orientation,
            state.velocity
        ]
        time_step = state.time_step
        return np.array(values), time_step

    def _array_to_state(self, x: np.array, time_step: int) -> YPState:
        """ Implementation of the VesselDynamics abstract method. """
        values = {
            'position': np.array([x[0], x[1]]),
            'orientation': x[2],
            'velocity': x[3],
        }
        state = YPState(**values, time_step=time_step)
        return state

    def _input_to_array(self, input: YPInputState) -> Tuple[np.array, int]:
        """ Implementation of the VesselDynamics abstract method. """
        values = [
            input.acceleration,
            input.yaw_rate
        ]
        time_step = input.time_step
        return np.array(values), time_step

    def _array_to_input(self, u: np.array, time_step: int) -> YPInputState:
        """ Implementation of the VesselDynamics abstract method. """
        values = {
            'acceleration': u[0],
            'yaw_rate': u[1]
        }
        return YPInputState(**values, time_step=time_step)
    
class YawVelocityConstrained(YawConstrained):
    def __init__(self, vessel_type: VesselType):
        super(YawVelocityConstrained, self).__init__(VesselModel.YP, vessel_type)

    def dynamics(self, t, x, u) -> List[float]:
        #consider velocity constraints
        u = velocity_constraints(x[3], u, self.parameters, t, vehicle_model=2, orientation = x[2])
        return vessel_dynamics_yp(x, u, self.parameters)

class ThreeDegreesOfFreedom(VesselDynamics):
    def __init__(self, vessel_type: VesselType):
        super(ThreeDegreesOfFreedom, self).__init__(VesselModel.TF, vessel_type)

    def dynamics(self, t, x, u) -> List[float]:
        return vessel_dynamics_3f(x, u, self.parameters)
    
    def _initialize_state(self, raw_state, time_step: int):
        raw_state_parse = {
            "position": [raw_state["position_x"], raw_state["position_y"]],
            "orientation": raw_state["orientation"], 
            "velocity": raw_state["velocity"],
            "velocity_y": raw_state["velocity_y"],
            "velocity_y": raw_state["velocity_y"],
            "yaw_rate": raw_state["yaw_rate"],
        }
        return TFState(**raw_state_parse, time_step=time_step)

    def _state_to_array(self, state: TFState) -> Tuple[np.array, int]:
        """ Implementation of the VesselDynamics abstract method. """

        values = [
            state.position[0],
            state.position[1],
            state.orientation,
            state.velocity,
            state.velocity_y,
            state.yaw_rate
        ]
        time_step = state.time_step
        return np.array(values), time_step

    def _array_to_state(self, x: np.array, time_step: int) -> TFState:
        """ Implementation of the VesselDynamics abstract method. """
        values = {
            'position': np.array([x[0], x[1]]),
            'orientation': x[2],
            'velocity': x[3],
            'velocity_y': x[4],
            'yaw_rate': x[5]
        }
        state = TFState(**values, time_step=time_step)
        return state

    def _input_to_array(self, input: TFInputState) -> Tuple[np.array, int]:
        """ Implementation of the VesselDynamics abstract method. """
        values = [
            input.force_orientation,
            input.force_lateral,
            input.yaw_moment
        ]
        time_step = input.time_step
        return np.array(values), time_step

    def _array_to_input(self, u: np.array, time_step: int) -> TFInputState:
        """ Implementation of the VesselDynamics abstract method. """
        values = {
            'force_orientation': u[0],
            'force_lateral': u[1],
            'yaw_moment': u[2]
        }
        return TFInputState(**values, time_step=time_step)