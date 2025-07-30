import enum
import math
import warnings
from abc import ABC, abstractmethod
from typing import Union, Set, List, Optional, Tuple
import numpy as np

from commonroad.geometry.shape import Shape, Rectangle, Circle, Polygon
from commonocean.prediction.prediction import Prediction, Occupancy, SetBasedPrediction, TrajectoryPrediction
from commonroad.scenario.state import State
from commonroad.common.validity import is_valid_orientation, is_real_number_vector, is_real_number

from commonocean.visualization.drawable import IDrawable
from commonocean.visualization.param_server import ParamServer
from commonocean.visualization.renderer import IRenderer


__author__ = "Hanna Krasowski"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"


@enum.unique
class ObstacleRole(enum.Enum):
    """ Enum containing all possible obstacle roles defined in CommonOcean."""
    STATIC = "static"
    DYNAMIC = "dynamic"


@enum.unique
class ObstacleType(enum.Enum):
    """ Enum containing all possible obstacle types defined in CommonOcean."""
    UNKNOWN = "unknown"
    BUOY = "buoy"
    LAND = "land"
    MOTORVESSEL = "motorvessel"
    SAILINGVESSEL = "sailingvessel"
    FISHINGVESSEL = "fishingvessel"
    MILITARYVESSEL = "militaryvessel"
    CARGOSHIP = "cargoship"
    VESSELNOTUNDERCOMMAND = "vesselNotUnderCommand"
    RESTRICTEDMANEUVERABILITYVESSEL = "restrictedManeuverabilityVessel"
    ANCHOREDVESSEL = "anchoredvessel"
    WINDFARM = "windfarm"
    OILRIG = "oilrig"
    WATERSBOUNDARY = "watersboundary"

class Obstacle(IDrawable):
    """ Superclass for dynamic and static obstacles holding common properties defined in CommonOcean."""

    def __init__(self, obstacle_id: int, obstacle_role: ObstacleRole,
                 obstacle_type: ObstacleType, obstacle_shape: Shape, initial_state: State, depth: float = None):
        """
        :param obstacle_id: unique ID of the obstacle
        :param obstacle_role: obstacle role as defined in CommonOcean
        :param obstacle_type: obstacle type as defined in CommonOcean (e.g. ANCHOREDVESSEL)
        :param obstacle_shape: occupied area of the obstacle
        :param initial_state: initial state of the obstacle
        :param depth: depth of the obstacle
        """
        self._initial_occupancy_shape: Shape = None

        self.obstacle_id: int = obstacle_id
        self.obstacle_role: ObstacleRole = obstacle_role
        self.obstacle_type: ObstacleType = obstacle_type
        self.obstacle_shape: Shape = obstacle_shape
        self.initial_state: State = initial_state

        if depth != None:
            self._depth = depth
        else:
            list_depth_inf = [ObstacleType.LAND, ObstacleType.BUOY, ObstacleType.UNKNOWN, ObstacleType.WINDFARM, ObstacleType.OILRIG]

            if isinstance(obstacle_shape, Rectangle):
                size = max(obstacle_shape.length, obstacle_shape.width)
            elif isinstance(obstacle_shape, Circle):
                size = 2*obstacle_shape.radius
            elif isinstance(obstacle_shape, Polygon):
                size = 0.0
                for vert1 in obstacle_shape.vertices:
                    for vert2 in obstacle_shape.vertices:
                        dist = np.linalg.norm(vert1-vert2)
                        if dist > size:
                            size = dist
            else:
                size = 0.0

            if obstacle_type not in list_depth_inf and size < 25:
                depth = 5.0
            elif obstacle_type not in list_depth_inf and size >= 25:
                depth = 15.0
            elif obstacle_type in list_depth_inf:
                depth = np.inf
            self._depth = depth

    def __hash__(self):
        return hash((self._obstacle_id, self._obstacle_role, self._obstacle_type, self._obstacle_shape,
                     self._initial_state))

    @property
    def obstacle_id(self) -> int:
        """ Unique ID of the obstacle."""
        return self._obstacle_id

    @property
    def obstacle_id(self) -> int:
        """ Unique ID of the obstacle."""
        return self._obstacle_id

    @obstacle_id.setter
    def obstacle_id(self, obstacle_id: int):
        assert isinstance(obstacle_id, int), '<Obstacle/obstacle_id>: argument obstacle_id of wrong type.' \
                                             'Expected type: %s. Got type: %s.' % (int, type(obstacle_id))
        if not hasattr(self, '_obstacle_id'):
            self._obstacle_id = obstacle_id
        else:
            warnings.warn('<Obstacle/obstacle_id>: Obstacle ID is immutable.')

    @property
    def obstacle_role(self) -> ObstacleRole:
        """ Obstacle role as defined in CommonOcean."""
        return self._obstacle_role

    @obstacle_role.setter
    def obstacle_role(self, obstacle_role: ObstacleRole):
        assert isinstance(obstacle_role, ObstacleRole), '<Obstacle/obstacle_role>: argument obstacle_role of wrong ' \
                                                        'type. Expected type: %s. Got type: %s.' \
                                                        % (ObstacleRole, type(obstacle_role))
        if not hasattr(self, '_obstacle_role'):
            self._obstacle_role = obstacle_role
        else:
            warnings.warn('<Obstacle/obstacle_role>: Obstacle role is immutable.')

    @property
    def obstacle_type(self) -> ObstacleType:
        """ Obstacle type as defined in CommonOcean."""
        return self._obstacle_type

    @obstacle_type.setter
    def obstacle_type(self, obstacle_type: ObstacleType):
        assert isinstance(obstacle_type, ObstacleType), '<Obstacle/obstacle_type>: argument obstacle_type of wrong ' \
                                                        'type. Expected type: %s. Got type: %s.' \
                                                        % (ObstacleType, type(obstacle_type))
        if not hasattr(self, '_obstacle_type'):
            self._obstacle_type = obstacle_type
        else:
            warnings.warn('<Obstacle/obstacle_type>: Obstacle type is immutable.')

    @property
    def obstacle_shape(self) -> Shape:
        """ Obstacle shape as defined in CommonOcean."""
        return self._obstacle_shape

    @obstacle_shape.setter
    def obstacle_shape(self, shape: Shape):
        assert isinstance(shape,
                          (type(None), Shape)), '<Obstacle/obstacle_shape>: argument shape of wrong type. Expected ' \
                                                'type %s. Got type %s.' % (Shape, type(shape))

        if not hasattr(self, '_obstacle_shape'):
            self._obstacle_shape = shape
        else:
            warnings.warn('<Obstacle/obstacle_shape>: Obstacle shape is immutable.')

    @property
    def initial_state(self) -> State:
        """ Initial state of the obstacle, e.g., obtained through sensor measurements."""
        return self._initial_state

    @initial_state.setter
    def initial_state(self, initial_state: State):
        assert isinstance(initial_state, State), '<Obstacle/initial_state>: argument initial_state of wrong type. ' \
                                                 'Expected types: %s. Got type: %s.' % (State, type(initial_state))
        self._initial_state = initial_state
        if not hasattr(initial_state, "orientation"):
                initial_state.orientation = math.atan2(initial_state.velocity_y, initial_state.velocity)
        self._initial_occupancy_shape = self._obstacle_shape.rotate_translate_local(
            initial_state.position, initial_state.orientation)

    @property
    def depth(self):
        """ Depth of the obstacle."""
        return self._depth
    
    @depth.setter
    def depth(self, depth: float):
        assert isinstance(depth, float), \
            '<Obstacle/depth>: argument depth of wrong ' \
            'type. Expected type: %s. Got type: %s.' \
            % (float, type(depth))
        assert depth >= 0, '<Obstacle/depth>: argument depth is a negative number. ' \
                           'Expected type is a positive number. Got: %s.' \
                           % (float, type(depth))
        self._depth = depth

    @property
    def initial_center_waters_ids(self) -> Union[None, Set[int]]:
        """ Initial waters of obstacle center, e.g., obtained through localization."""
        return self._initial_center_waters_ids

    @initial_center_waters_ids.setter
    def initial_center_waters_ids(self, initial_center_waters_ids: Union[None, Set[int]]):
        assert isinstance(initial_center_waters_ids, (set, type(None))), \
            '<Obstacle/initial_center_waters_ids>: argument initial_waters_ids of wrong type. ' \
            'Expected types: %s, %s. Got type: %s.' % (set, type(None), type(initial_center_waters_ids))
        if initial_center_waters_ids is not None:
            for waters_id in initial_center_waters_ids:
                assert isinstance(waters_id, int), \
                    '<Obstacle/initial_center_waters_ids>: argument initial_waters of wrong type. ' \
                    'Expected types: %s. Got type: %s.' % (int, type(waters_id))
        self._initial_center_waters_ids = initial_center_waters_ids

    @property
    def initial_shape_waters_ids(self) -> Union[None, Set[int]]:
        """ Initial waters of obstacle shape, e.g., obtained through localization."""
        return self._initial_shape_waters_ids

    @initial_shape_waters_ids.setter
    def initial_shape_waters_ids(self, initial_shape_waters_ids: Union[None, Set[int]]):
        assert isinstance(initial_shape_waters_ids, (set, type(None))), \
            '<Obstacle/initial_shape_waters_ids>: argument initial_waters_ids of wrong type. ' \
            'Expected types: %s, %s. Got type: %s.' % (set, type(None), type(initial_shape_waters_ids))
        if initial_shape_waters_ids is not None:
            for waters_id in initial_shape_waters_ids:
                assert isinstance(waters_id, int), \
                    '<Obstacle/initial_shape_waters_ids>: argument initial_waters of wrong type. ' \
                    'Expected types: %s. Got type: %s.' % (int, type(waters_id))
        self._initial_shape_waters_ids = initial_shape_waters_ids

    @abstractmethod
    def occupancy_at_time(self, time_step: int) -> Union[None, Occupancy]:
        pass

    @abstractmethod
    def translate_rotate(self, translation: np.ndarray, angle: float):
        pass


class StaticObstacle(Obstacle):
    """ Class representing static obstacles as defined in CommonOcean."""

    def __init__(self, obstacle_id: int, obstacle_type: ObstacleType,
                 obstacle_shape: Shape, initial_state: State, depth: float = None):
        """
            :param obstacle_id: unique ID of the obstacle
            :param obstacle_type: type of obstacle (e.g. ANCHOREDVESSEL)
            :param obstacle_shape: shape of the static obstacle
            :param initial_state: initial state of the static obstacle
        """
        Obstacle.__init__(self, obstacle_id=obstacle_id, obstacle_role=ObstacleRole.STATIC,
                          obstacle_type=obstacle_type, obstacle_shape=obstacle_shape, initial_state=initial_state, depth=depth)

    def translate_rotate(self, translation: np.ndarray, angle: float):
        """ First translates the static obstacle, then rotates the static obstacle around the origin.

            :param translation: translation vector [x_off, y_off] in x- and y-direction
            :param angle: rotation angle in radian (counter-clockwise)
        """
        assert is_real_number_vector(translation, 2), '<StaticObstacle/translate_rotate>: argument translation is ' \
                                                      'not a vector of real numbers of length 2.'
        assert is_real_number(angle), '<StaticObstacle/translate_rotate>: argument angle must be a scalar. ' \
                                      'angle = %s' % angle
        assert is_valid_orientation(angle), '<StaticObstacle/translate_rotate>: argument angle must be within the ' \
                                            'interval [-2pi, 2pi]. angle = %s' % angle
        self.initial_state = self._initial_state.translate_rotate(translation, angle)

    def occupancy_at_time(self, time_step: int) -> Occupancy:
        """
        Returns the predicted occupancy of the obstacle at a specific time step.

        :param time_step: discrete time step
        :return: occupancy of the static obstacle at time step
        """
        return Occupancy(time_step=time_step, shape=self._initial_occupancy_shape)

    def state_at_time(self, time_step: int) -> State:
        """
        Returns the state the obstacle at a specific time step.

        :param time_step: discrete time step
        :return: state of the static obstacle at time step
        """
        return self.initial_state

    def __str__(self):
        obs_str = 'Static Obstacle:\n'
        obs_str += '\nid: {}'.format(self.obstacle_id)
        obs_str += '\ninitial state: {}'.format(self.initial_state)
        return obs_str

    def draw(self, renderer: IRenderer,
             draw_params: Union[ParamServer, dict, None] = None):
        renderer.draw_static_obstacle(self, draw_params)


class DynamicObstacle(Obstacle):
    """ Class representing dynamic obstacles as defined in CommonOcean. Each dynamic obstacle has stored its predicted
    movement in future time steps.
    """

    def __init__(self, obstacle_id: int, obstacle_type: ObstacleType,
                 obstacle_shape: Shape, initial_state: State,
                 prediction: Union[None, Prediction, TrajectoryPrediction, SetBasedPrediction] = None, depth: float = None):
        """
            :param obstacle_id: unique ID of the obstacle
            :param obstacle_type: type of obstacle (e.g. PARKED_VEHICLE)
            :param obstacle_shape: shape of the static obstacle
            :param initial_state: initial state of the static obstacle
            :param prediction: predicted movement of the dynamic obstacle
            """
        Obstacle.__init__(self, obstacle_id=obstacle_id, obstacle_role=ObstacleRole.DYNAMIC,
                          obstacle_type=obstacle_type, obstacle_shape=obstacle_shape, initial_state=initial_state, depth = depth)
        self.prediction: Prediction = prediction

    @property
    def prediction(self) -> Union[Prediction, TrajectoryPrediction, SetBasedPrediction, None]:
        """ Prediction describing the movement of the dynamic obstacle over time."""
        return self._prediction

    @prediction.setter
    def prediction(self, prediction: Union[Prediction, TrajectoryPrediction, SetBasedPrediction, None]):
        assert isinstance(prediction, (Prediction, type(None))), '<DynamicObstacle/prediction>: argument prediction ' \
                                                                 'of wrong type. Expected types: %s, %s. Got type: ' \
                                                                 '%s.' % (Prediction, type(None), type(prediction))
        self._prediction = prediction

    def occupancy_at_time(self, time_step: int) -> Union[None, Occupancy]:
        """
        Returns the predicted occupancy of the obstacle at a specific time step.

        :param time_step: discrete time step
        :return: predicted occupancy of the obstacle at time step
        """
        occupancy = None

        if time_step == self.initial_state.time_step:
            occupancy = Occupancy(time_step, self._initial_occupancy_shape)
        elif time_step > self.initial_state.time_step and self._prediction is not None:
            occupancy = self._prediction.occupancy_at_time_step(time_step)
        return occupancy

    def state_at_time(self, time_step: int) -> Union[None, State]:
        """
        Returns the predicted state of the obstacle at a specific time step.

        :param time_step: discrete time step
        :return: predicted state of the obstacle at time step
        """
        if time_step == self.initial_state.time_step:
            return self.initial_state
        elif type(self._prediction) is SetBasedPrediction:
            warnings.warn("<DynamicObstacle/state_at_time>: Set-based prediction is used. CustomState cannot be returned!")
            return None
        elif time_step > self.initial_state.time_step and self._prediction is not None:
            return self.prediction.trajectory.state_at_time_step(time_step)
        else:
            return None

    def translate_rotate(self, translation: np.ndarray, angle: float):
        """ First translates the dynamic obstacle, then rotates the dynamic obstacle around the origin.

        :param translation: translation vector [x_off, y_off] in x- and y-direction
        :param angle: rotation angle in radian (counter-clockwise)
        """
        assert is_real_number_vector(translation, 2), '<DynamicObstacle/translate_rotate>: argument translation is ' \
                                                      'not a vector of real numbers of length 2.'
        assert is_real_number(angle), '<DynamicObstacle/translate_rotate>: argument angle must be a scalar. ' \
                                      'angle = %s' % angle
        assert is_valid_orientation(angle), '<DynamicObstacle/translate_rotate>: argument angle must be within the ' \
                                            'interval [-2pi, 2pi]. angle = %s' % angle
        if self._prediction is not None:
            self.prediction.translate_rotate(translation, angle)

        self.initial_state = self._initial_state.translate_rotate(translation, angle)

    def extreme_limits(self) -> List[List[float]]:

        """ Calculate the extreme limits that the obstacle reaches during the movement.

        :return: List of the extreme limits of the obstacle in the form [[max_x, min_x], [max_y, min_y]]
        """
 
        flag = True
        for occupancy in self.prediction.occupancy_set:
            if not flag:
                x = occupancy.shape.center[0]
                y = occupancy.shape.center[1]
                if x > max_x:
                    max_x = x
                if x < min_x:
                    min_x = x
                if y > max_y:
                    max_y = y
                if y < min_y:
                    min_y = y
            else:
                max_x = occupancy.shape.center[0]
                max_y = occupancy.shape.center[1]
                min_x = max_x
                min_y = max_y
                flag = False

        return [[max_x, min_x], [max_y, min_y]]

    def __str__(self):
        obs_str = 'Dynamic Obstacle:\n'
        obs_str += '\nid: {}'.format(self.obstacle_id)
        obs_str += '\ninitial state: {}'.format(self.initial_state)
        return obs_str

    def draw(self, renderer: IRenderer,
             draw_params: Union[ParamServer, dict, None] = None):
        renderer.draw_dynamic_obstacle(self, draw_params)

