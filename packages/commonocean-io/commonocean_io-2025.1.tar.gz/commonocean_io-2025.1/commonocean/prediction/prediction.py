__author__ = "Bruno Maione"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2023a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "development"

import math
from typing import Union, List, Dict, Set
import numpy as np

from commonroad.common.util import Interval
from commonroad.common.validity import is_valid_orientation, is_real_number_vector
from commonroad.geometry.shape import Shape, \
    occupancy_shape_from_state
from commonocean.scenario.trajectory import Trajectory
from commonroad.prediction.prediction import Occupancy as Occupancy_CR
from commonroad.prediction.prediction import Prediction as Prediction_CR

class Occupancy(Occupancy_CR):
    """ Class describing an occupied area in the position domain. The
    occupied area can be defined for a certain time
    step or a time interval."""

    def __init__(self, time_step: Union[int, Interval], shape: Shape):
        """
        :param time_step: a time interval or time step for which the
        occupancy is defined
        :param shape: occupied region in the position domain
        """
        super().__init__(time_step, shape)

class Prediction(Prediction_CR):
    """
    Base class for a prediction module.
    """
    def __init__(self, initial_time_step: int, occupancy_set: List[Occupancy]):
        """
        :param initial_time_step: initial time step of the prediction
        :param occupancy_set: list of occupancies defined for different time steps or time intervals.
        """
        super().__init__(initial_time_step, occupancy_set)

class SetBasedPrediction(Prediction):
    """ Class to represent the future behavior of obstacles by bounded occupancy sets."""
    def __init__(self, initial_time_step: int, occupancy_set: List[Occupancy]):
        """
        :param initial_time_step: initial time step of the set-based prediction
        :param occupancy_set: list of occupancies defined for different time steps or time intervals.
        """
        Prediction.__init__(self, initial_time_step, occupancy_set)

    def translate_rotate(self, translation: np.ndarray, angle: float):
        """ Translates and rotates the occupancy set.

        :param translation: translation vector [x_off, y_off] in x- and y-direction
        :param angle: rotation angle in radian (counter-clockwise)
        """
        assert is_real_number_vector(translation, 2), '<SetBasedPrediction/translate_rotate>: argument "translation" ' \
                                                      'is not a vector of real numbers of length 2.'
        assert is_valid_orientation(angle), '<SetBasedPrediction/translate_rotate>: argument "orientation" ' \
                                            'is not valid.'
        for occ in self._occupancy_set:
            occ.translate_rotate(translation, angle)


class TrajectoryPrediction(Prediction):
    """ Class to represent the predicted movement of an obstacle using a trajectory. A trajectory is modeled as a
    state sequence over time. The occupancy of an obstacle along a trajectory is uniquely defined given its shape."""
    def __init__(self, trajectory: Trajectory, shape: Shape,
                 center_waters_assignment: Union[None, Dict[int, Set[int]]] = None,
                 shape_waters_assignment: Union[None, Dict[int, Set[int]]] = None):
        """
        :param trajectory: predicted trajectory of the obstacle
        :param shape: shape of the obstacle
        """
        self.shape: Shape = shape
        self.trajectory: Trajectory = trajectory
        self.shape_waters_assignment: Dict[int, Set[int]] = shape_waters_assignment
        self.center_waters_assignment: Dict[int, Set[int]] = center_waters_assignment
        Prediction.__init__(self, self._trajectory.initial_time_step, self._create_occupancy_set())

    @property
    def shape(self) -> Shape:
        """ Shape of the predicted object."""
        return self._shape

    @shape.setter
    def shape(self, shape: Shape):
        assert isinstance(shape, Shape), '<TrajectoryPrediction/shape>: argument "shape" of wrong type. Expected ' \
                                         'type: %s. Got type: %s.' % (Shape, type(shape))
        self._shape = shape

    @property
    def trajectory(self) -> Trajectory:
        """ Predicted trajectory of the object."""
        return self._trajectory

    @trajectory.setter
    def trajectory(self, trajectory: Trajectory):
        assert isinstance(trajectory, Trajectory), '<TrajectoryPrediction/trajectory>: argument "trajectory" of wrong' \
                                                   ' type. Expected type: %s. Got type: %s.' \
                                                   % (Trajectory, type(trajectory))
        self._trajectory = trajectory

    @property
    def shape_waters_assignment(self) -> Union[None, Dict[int, Set[int]]]:
        """ Predicted waters assignment of obstacle shape."""
        return self._shape_waters_assignment

    @shape_waters_assignment.setter
    def shape_waters_assignment(self, shape_waters_assignment: Union[None, Dict[int, Set[int]]]):
        if shape_waters_assignment is not None:
            assert isinstance(shape_waters_assignment, dict), '<TrajectoryPrediction/shape_waters_assignment>: ' \
                                                         'argument "shape_waters_assignment" of wrong type. ' \
                                                               'Expected type: %s. Got' \
                                                               ' type: %s.' % (Dict, type(shape_waters_assignment))
        self._shape_waters_assignment = shape_waters_assignment

    @property
    def center_waters_assignment(self) -> Union[None, Dict[int, Set[int]]]:
        """ Predicted waters assignment of obstacle center."""
        return self._center_waters_assignment

    @center_waters_assignment.setter
    def center_waters_assignment(self, center_waters_assignment: Union[None, Dict[int, Set[int]]]):
        if center_waters_assignment is not None:
            assert isinstance(center_waters_assignment, dict), '<TrajectoryPrediction/center_waters_assignment>: ' \
                                                         'argument "center_waters_assignment" of wrong type. ' \
                                                         'Expected type: ' \
                                                         '%s. Got type: %s.' % (Dict, type(center_waters_assignment))
        self._center_waters_assignment = center_waters_assignment

    def translate_rotate(self, translation: np.ndarray, angle: float):
        """ Translates and rotates all states of the trajectory and re-computes the translated and rotated occupancy
        set.

        :param translation: translation vector [x_off, y_off] in x- and y-direction
        :param angle: rotation angle in radian (counter-clockwise)
        """
        assert is_real_number_vector(translation, 2), '<TrajectoryPrediction/translate_rotate>: argument ' \
                                                      '"translation" is not a vector of real numbers of length 2.'
        assert is_valid_orientation(angle), '<TrajectoryPrediction/translate_rotate>: argument "orientation" is ' \
                                            'not valid.'

        self._trajectory.translate_rotate(translation, angle)
        self._occupancy_set = self._create_occupancy_set()

    def _create_occupancy_set(self):
        """ Computes the occupancy set over time given the predicted trajectory and shape of the object."""
        occupancy_set = list()
        for k, state in enumerate(self._trajectory.state_list):
            if not hasattr(state, "orientation"):
                state.orientation = math.atan2(state.velocity_y, state.velocity)
            occupied_region = occupancy_shape_from_state(self._shape, state)
            occupancy_set.append(Occupancy(state.time_step, occupied_region))
        return occupancy_set
