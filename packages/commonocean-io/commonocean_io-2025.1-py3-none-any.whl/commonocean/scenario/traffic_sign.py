import enum
from typing import List, Union
import numpy as np

from commonroad.common.validity import *
import commonroad.geometry.transform

__author__ = "Hanna Krasowski, Benedikt Pfleiderer, Fabian Thomas-Barein"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"


@enum.unique
class TrafficSignElementID(enum.Enum):
    LATERAL_MARK_RED_A = '101'
    LATERAL_MARK_GREEN_A = '102'
    SPECIAL_MARK = '103'
    CARDINAL_MARK_NORTH = '104'
    CARDINAL_MARK_EAST = '105'
    CARDINAL_MARK_SOUTH = '106'
    CARDINAL_MARK_WEST = '107'



class TrafficSignElement:
    """ Class which represents a collection of traffic signs at one position"""

    def __init__(self, traffic_sign_element_id: Union[TrafficSignElementID],
                 additional_values: List[str]):
        """

        :param traffic_sign_element_id: ID of traffic sign element (must be element of a traffic sign element enum)
        :param additional_values: list of additional values of a traffic sign element, e.g. velocity limit, lightning pattern, name
        """
        self._traffic_sign_element_id = traffic_sign_element_id
        self._additional_values = additional_values

    @property
    def traffic_sign_element_id(self) -> TrafficSignElementID:
        """ Returns the ID of the traffic sign element"""
        return self._traffic_sign_element_id

    @property
    def additional_values(self) -> List[str]:
        """ Returns the additional values of the traffic sign element"""
        return self._additional_values

    def __eq__(self, other: 'TrafficSignElement'):
        if self.traffic_sign_element_id == other.traffic_sign_element_id \
                and self.additional_values == other.additional_values:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self._traffic_sign_element_id) + str(self.additional_values))

    def __str__(self):
        return f"Sign Element with id {self._traffic_sign_element_id} and values {self._additional_values} "

    def __repr__(self):
        return f"Sign Element with id {self._traffic_sign_element_id} and values {self._additional_values} "


class TrafficSign:
    """Class to represent a traffic sign"""

    def __init__(self, traffic_sign_id: int, traffic_sign_elements: List[TrafficSignElement],
                 position: np.ndarray, virtual: bool = False, related_obstacle: Union[None, int] = None):
        """
        :param traffic_sign_id: ID of traffic sign
        :param traffic_sign_elements: list of traffic sign elements
        :param position: position of traffic sign
        :param virtual: boolean indicating if this traffic sign is also placed there in the real environment or it
        is added for other reasons (e.g., completeness of scenario)
        :param related_obstacle: ID of the obstacle related to the traffic sign
        """
        self._traffic_sign_id = traffic_sign_id
        self._position = position
        self._traffic_sign_elements = traffic_sign_elements
        self._virtual = virtual
        self._related_obstacle = related_obstacle

    def __eq__(self, other):
        if not isinstance(other, TrafficSign):
            warnings.warn(f"Inequality between TrafficSign {repr(self)} and different type {type(other)}")
            return False

        list_elements_eq = True
        traffic_sign_elements = {traffic_sign_element.traffic_sign_element_id: traffic_sign_element
                                 for traffic_sign_element in self._traffic_sign_elements}
        traffic_sign_elements_other = {traffic_sign_element.traffic_sign_element_id: traffic_sign_element
                                       for traffic_sign_element in other._traffic_sign_elements}
        traffic_sign_eq = len(traffic_sign_elements) == len(traffic_sign_elements_other)
        for k in traffic_sign_elements.keys():
            if k not in traffic_sign_elements_other:
                traffic_sign_eq = False
                continue
            if traffic_sign_elements.get(k) != traffic_sign_elements_other.get(k):
                list_elements_eq = False

        position_string = None if self._position is None else \
            np.array2string(np.around(self._position.astype(float), 10), precision=10)
        position_other_string = None if other._position is None else \
            np.array2string(np.around(other.position.astype(float), 10), precision=10)

        if traffic_sign_eq and self._traffic_sign_id == other.traffic_sign_id \
                and position_string == position_other_string and self._virtual == other.virtual:
            return list_elements_eq

        warnings.warn(f"Inequality of TrafficSign {repr(self)} and the other one {repr(other)}")
        return False

    def __hash__(self):
        position_string = None if self._position is None else \
            np.array2string(np.around(self._position.astype(float), 10), precision=10)
        return hash((self._traffic_sign_id, position_string, frozenset(self._traffic_sign_elements), self._virtual))


    def __repr__(self):
        return f"TrafficSign(traffic_sign_id={self._traffic_sign_id}, " \
               f"traffic_sign_elements={repr(self._traffic_sign_elements)}, " \
               f"position={None if self._position is None else self._position.tolist()}, virtual={self._virtual})"

    def __str__(self):
        return f"Sign At {self._position} with {self._traffic_sign_elements} "


    @property
    def traffic_sign_id(self) -> int:
        """ Returns the ID of the traffic sign"""
        return self._traffic_sign_id

    @property
    def position(self) -> Union[None, np.ndarray]:
        """ Returns the position of the traffic sign"""
        return self._position

    @property
    def traffic_sign_elements(self) -> List[TrafficSignElement]:
        """ Returns the list of traffic sign elements"""
        return self._traffic_sign_elements

    @property
    def virtual(self) -> bool:
        """ Returns if the traffic sign is virtual or not"""
        return self._virtual

    @property
    def related_obstacle(self) -> Union[None, int]:
        """ Returns the ID of the obstacle related to the traffic sign"""
        return self._related_obstacle

    @related_obstacle.setter
    def related_obstacle(self, obstacle_id: int):
        self._related_obstacle = obstacle_id

    def translate_rotate(self, translation: np.ndarray, angle: float):
        """
        This method translates and rotates a traffic sign

        :param translation: The translation given as [x_off,y_off] for the x and y translation
        :param angle: The rotation angle in radian (counter-clockwise defined)
        """

        assert is_real_number_vector(translation, 2), '<TrafficSign/translate_rotate>: argument translation is ' \
                                                      'not a vector of real numbers of length 2.'
        assert is_real_number(angle), '<TrafficSign/translate_rotate>: argument angle must be a scalar. ' \
                                      'angle = %s' % angle
        assert is_valid_orientation(angle), '<TrafficSign/translate_rotate>: argument angle must be within the ' \
                                            'interval [-2pi, 2pi]. angle = %s' % angle
        self._position = commonroad.geometry.transform.translate_rotate(np.array([self._position]),
                                                                        translation, angle)[0]
