import copy
import math
from typing import Union, List, Dict, Set
import numpy as np
import warnings

from commonroad.geometry.shape import Shape
from commonroad.scenario.state import State
from commonroad.common.util import Interval, AngleInterval
from commonocean.scenario.obstacle import StaticObstacle, DynamicObstacle

from commonocean.visualization.drawable import IDrawable
from commonocean.visualization.param_server import ParamServer
from commonocean.visualization.renderer import IRenderer


__author__ = "Hanna Krasowski, Benedikt Pfleiderer, Fabian Thomas-Barein"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"


class GoalRegion(IDrawable):
    def __init__(self, state_list: List[State],
                 waters_of_goal_position: Union[None, Dict[int, List[int]]] = None):
        """
        Region, that has to be reached by the vessel. Contains a list of goal states of which one has to be fulfilled
        to solve the scenario. If 'position' in a goal state is given as a list of waters, they are converted into a
        polygon. To reconstruct the waters later, the water ids are stored in a dict in waters_of_goal_position.
        In no 'position' is given as water, waters_of_goal_position is set to None.

        :param state_list: list of goal states (one of those has to be fulfilled)
        :param waters_of_goal_position: dict[index of state in state_list, list of water ids].
        None, if no water is given.
        """
        self.state_list = state_list
        self.waters_of_goal_position = waters_of_goal_position

    @property
    def state_list(self) -> List[State]:
        """List that contains all goal states"""
        return self._state_list

    @state_list.setter
    def state_list(self, state_list: List[State]):
        for state in state_list:
            self._validate_goal_state(state)
        self._state_list = state_list

    @property
    def waters_of_goal_position(self) -> Union[None, Dict[int, List[int]]]:
        """Dict that contains the index of the state in the state_list to which the waters belong. \
        None, if goal position is not a water"""
        return self._waters_of_goal_position

    @waters_of_goal_position.setter
    def waters_of_goal_position(self, waters: Union[None, Dict[int, List[int]]]):
        if not hasattr(self, '_waters_of_goal_position'):
            if waters is not None:
                assert isinstance(waters, dict)
                assert all(isinstance(x, int) for x in waters.keys())
                assert all(isinstance(x, list) for x in waters.values())
                assert all(isinstance(x, int) for waters_list in waters.values() for x in waters_list)
            self._waters_of_goal_position = waters
        else:
            warnings.warn('<GoalRegion/waters_of_goal_position> waters_of_goal_position are immutable')

    def is_reached(self, state: State, prev_state: State = None, vessel_parameters = None) -> bool:
        """
        Checks if a given state is inside the goal region.

        :param state: state with exact values
        :return: True, if state fulfills all requirements of the goal region. False if at least one requirement of the \
        goal region is not fulfilled.
        """
        is_reached_list = list()
        for goal_state in self.state_list:
            goal_state_tmp = copy.deepcopy(goal_state)
            goal_state_fields = set(goal_state.used_attributes)
            state_fields = set(state.used_attributes)
            state_new, state_fields, goal_state_tmp, goal_state_fields = \
                self._harmonize_state_types(state, goal_state_tmp, state_fields, goal_state_fields)

            if prev_state is not None:
                prev_state_new, _, _, _ = \
                    self._harmonize_state_types(prev_state, goal_state_tmp, state_fields, goal_state_fields)

            if not goal_state_fields.issubset(state_fields):
                raise ValueError('The goal states {} are not a subset of the provided states {}!'
                                 .format(goal_state_fields, state_fields))
            is_reached = True
            if hasattr(goal_state, 'time_step'):
                is_reached = is_reached and self._check_value_in_interval(state_new.time_step, goal_state.time_step)
            if hasattr(goal_state, 'position'):
                is_reached = is_reached and goal_state.position.contains_point(state_new.position)
            if hasattr(goal_state, 'orientation'):
                is_reached = is_reached and self._check_value_in_interval(state_new.orientation, goal_state.orientation)
            if hasattr(goal_state, 'velocity'):
                is_reached = is_reached and self._check_value_in_interval(state_new.velocity, goal_state.velocity)
            is_reached_list.append(is_reached)
        return np.any(is_reached_list)

    def translate_rotate(self, translation: np.ndarray, angle: float):
        """
        translate and rotates the goal region with given translation and angle around the origin (0, 0)

        :param translation: translation vector [x_off, y_off] in x- and y-direction
        :param angle: rotation angle in radian (counter-clockwise)
        """
        for i, state in enumerate(self.state_list):
            self.state_list[i] = state.translate_rotate(translation, angle)

    @classmethod
    def _check_value_in_interval(cls, value: Union[int, float], desired_interval: Union[AngleInterval, Interval]) -> \
            bool:
        """
        Checks if an exact value is included in the desired interval. If desired_interval is not an interval,
        an exception is thrown.

        :param value: int or float value to test
        :param desired_interval: Desired interval in which value is tested
        :return: True, if value matches the desired_value, False if not.
        """
        if isinstance(desired_interval, (Interval, AngleInterval)):
            is_reached = desired_interval.contains(value)
        else:
            raise ValueError("<GoalRegion/_check_value_in_interval>: argument 'desired_interval' of wrong type. "
                             "Expected type: {}. Got type: {}.".format((type(Interval), type(AngleInterval)),
                                                                       type(desired_interval)))
        return is_reached

    @classmethod
    def _validate_goal_state(cls, state: State):
        """
        Checks if state fulfills the requirements for a goal state and raises Error if not.

        :param state: state to check
        """
        
        if not hasattr(state, 'time_step'):
            raise ValueError('<GoalRegion/_goal_state_is_valid> field time_step is mandatory. '
                             'No time_step attribute found.')

        
        valid_fields = ['time_step', 'position', 'velocity', 'orientation']

        for attr in state.used_attributes:
            if attr not in valid_fields:
                raise ValueError('<GoalRegion/_goal_state_is_valid> field error: allowed fields are '
                                 '[time_step, position, velocity, orientation]; "%s" detected' % attr)
            elif attr == 'position':
                if not isinstance(getattr(state, attr), Shape):
                    raise ValueError(
                        '<GoalRegion/_goal_state_is_valid> position needs to be an instance of '
                        '%s; got instance of %s instead' % (Shape, getattr(state, attr).__class__))
            elif attr == 'orientation':
                if not isinstance(getattr(state, attr), AngleInterval):
                    raise ValueError('<GoalRegion/_goal_state_is_valid> orientation needs to be an instance of %s; got '
                                     'instance of %s instead' % (AngleInterval, getattr(state, attr).__class__))
            else:
                if not isinstance(getattr(state, attr), Interval):
                    raise ValueError('<GoalRegion/_goal_state_is_valid> attributes must be instances of '
                                     '%s only (except from position and orientation); got "%s" for '
                                     'attribute "%s"' % (Interval, getattr(state, attr).__class__, attr))

    def _harmonize_state_types(self, state: State, goal_state: State, state_fields: Set[str],
                               goal_state_fields: Set[str]):
        """
        Transforms states from value_x, value_y to orientation, value representation if required.
        
        :param state: state to check for goal
        :param goal_state: goal state
        :return: state_new, state_fields, goal_state, goal_state_fields
        """
        state_new = copy.deepcopy(state)
        if {'velocity', 'velocity_y'}.issubset(state_fields) \
                and {'orientation'}.issubset(goal_state_fields) \
                and not {'velocity', 'velocity_y'}.issubset(goal_state_fields):

            if not 'orientation' in state_fields:
                state_new.orientation = math.atan2(state_new.velocity_y, state_new.velocity)
                state_fields.add('orientation')

            state_new.velocity = np.linalg.norm(np.array([state_new.velocity, state_new.velocity_y]))
            state_fields.remove('velocity_y')

        return state_new, state_fields, goal_state, goal_state_fields

    def draw(self, renderer: IRenderer, draw_params: Union[ParamServer, dict, None] = None):
        renderer.draw_goal_region(self, draw_params)

