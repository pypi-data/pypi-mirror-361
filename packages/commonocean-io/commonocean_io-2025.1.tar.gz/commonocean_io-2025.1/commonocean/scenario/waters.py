import enum
from typing import *
from uuid import RESERVED_FUTURE
import numpy as np
import abc

from commonroad.geometry.shape import Circle, Rectangle, Shape, Polygon, ShapeGroup
from commonroad.geometry.transform import translation_rotation_matrix
from commonroad.common.validity import *

from commonocean.scenario.obstacle import Obstacle
from commonocean.scenario.traffic_sign import TrafficSign

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


class WatersType(enum.Enum):
    """
    Enum describing different types of waters
    """
    UNKNOWN = 'unknown'
    FAIRWAY = 'fairway'
    SHALLOW = 'shallow'
    TRAFFICSEPARATIONZONE = 'trafficseparationzone'

    
class Waters(metaclass=abc.ABCMeta):
    """
    Abstract class for waters in CommonOcean
    """

    @property
    def waters_type(self):
        """ Type of the waters """
        pass

    @property
    def waters_id(self):
        """ ID of the waters """
        pass

    @abc.abstractmethod
    def translate_rotate(self, translation: np.ndarray, angle: float):
        """ Translates and rotates the waters """
        pass

    @abc.abstractmethod
    def contains_points(self, point: np.ndarray):
        """ Checks if a point is enclosed in the waters """
        pass

    @abc.abstractmethod
    def get_obstacles(self):
        """ Returns the subset of obstacles, which are located in the waters """
        pass


class Waterway(Waters):

    """
    Class which describes a Waters entity according to the CommonOcean specification.
    """

    def __init__(self, left_vertices: np.ndarray, center_vertices: np.ndarray, right_vertices: np.ndarray,
                 waters_id: int, waters_type: WatersType, predecessor=None, successor=None,
                 traffic_signs=None, depth: float = np.inf
                 ):
        """
        Constructor of a Waters object
        :param left_vertices: The vertices of the left boundary of the Waters described as a
        polyline [[x0,x1,...,xn],[y0,y1,...,yn]]
        :param center_vertices: The vertices of the center line of the Waters described as a
        polyline [[x0,x1,...,xn],[y0,y1,...,yn]]
        :param right_vertices: The vertices of the right boundary of the Waters described as a
        polyline [[x0,x1,...,xn],[y0,y1,...,yn]]
        :param waters_id: The unique id (natural number) of the water
        :param waters_type: Class of Water
        :param predecessor: The list of predecessor waters (None if not existing)
        :param successor: The list of successor waters (None if not existing)
        :param traffic_signs: Traffic signs to be applied
        :param depth: The depth of the water in meters (default: np.inf)
        """

        self._left_vertices = None
        self._right_vertices = None
        self._center_vertices = None
        self._waters_id = None

        self.waters_id = waters_id
        self.left_vertices = left_vertices
        self.right_vertices = right_vertices
        self.center_vertices = center_vertices
        assert len(left_vertices[0]) == len(center_vertices[0]) == len(
            right_vertices[0]), '<Waters/init>: Provided polylines do not share the same length! {}/{}/{}'.format(
            len(left_vertices[0]), len(center_vertices[0]), len(right_vertices[0]))

        assert (waters_type == WatersType.FAIRWAY or waters_type == WatersType.TRAFFICSEPARATIONZONE or WatersType.UNKNOWN), \
        '<Waters/init>: Waterway must be of type traffic separation zone, fairway or unknown. Got type {}'.format(waters_type)
        self._waters_type = waters_type

        self._predecessor = None
        if predecessor is None:
            self._predecessor = []
        else:
            self.predecessor = predecessor
        self._successor = None
        if successor is None:
            self._successor = []
        else:
            self.successor = successor

        self._polygon = None

        self._traffic_signs = None
        if traffic_signs is None:
            self._traffic_signs = set()
        else:
            self.traffic_signs = traffic_signs
        
        self._depth = depth

    def __eq__(self, other):
        if not isinstance(other, Waters):
            warnings.warn(f"Inequality between Waters {repr(self)} and different type {type(other)}")
            return False

        waters_eq = True
        polylines = [self._left_vertices, self._right_vertices, self._center_vertices]
        polylines_other = [other.left_vertices, other.right_vertices, other.center_vertices]

        for i in range(0, len(polylines)):
            polyline = polylines[i]
            polyline_other = polylines_other[i]
            polyline_string = np.array2string(np.around(polyline.astype(float), 10), precision=10)
            polyline_other_string = np.array2string(np.around(polyline_other.astype(float), 10), precision=10)
            waters_eq = waters_eq and polyline_string == polyline_other_string

        if waters_eq and self.waters_id == other.waters_id \
                and set(self._predecessor) == set(other.predecessor) and set(self._successor) == set(other.successor) \
                and self._waters_type == other.waters_type \
                and self._traffic_signs == other.traffic_signs:
            return polylines

        warnings.warn(f"Inequality of Waters {repr(self)} and the other one {repr(other)}")
        return False

    def __hash__(self):
        polylines = [self._left_vertices, self._right_vertices, self._center_vertices]
        polyline_strings = []
        for polyline in polylines:
            polyline_string = np.array2string(np.around(polyline.astype(float), 10), precision=10)
            polyline_strings.append(polyline_string)

        elements = [self._predecessor, self._successor, self._traffic_signs]
        frozen_elements = [frozenset(e) for e in elements]
        frozen_elements.append(self._waters_type)

        return hash((self._waters_id, tuple(polyline_strings), tuple(frozen_elements)))

    def __str__(self):
        return 'Waterway with id:' + str(self.waters_id)
        
    def __repr__(self):
        return f"Waterway(left_vertices={self._left_vertices.tolist()}, " \
               f"center_vertices={self._center_vertices.tolist()}, " \
               f"right_vertices={self._right_vertices.tolist()}, waters_id={self._waters_id}, " \
               f"predecessor={self._predecessor}, successor={self._successor}, " \
               f"waters_type={self._waters_type}, " \
               f" traffic_signs={self._traffic_signs}, " \
                f"depth={self._depth}"

    @property
    def waters_type(self) -> WatersType:
        """ Type of the waters """
        return self._waters_type

    @property
    def waters_id(self) -> int:
        """ ID of the waters """
        return self._waters_id

    @waters_id.setter
    def waters_id(self, f_id: int):
        if self._waters_id is None:
            assert is_natural_number(f_id), '<Waters/waters_id>: Provided waters_id is not valid! id={}'.format(f_id)
            self._waters_id = f_id
        else:
            warnings.warn('<Waters/waters_id>: waters_id of waters is immutable')

    @property
    def left_vertices(self) -> np.ndarray:
        """ Left vertices of the waters """
        return self._left_vertices

    @left_vertices.setter
    def left_vertices(self, polyline: np.ndarray):
        if self._left_vertices is None:
            assert is_valid_polyline(
                polyline), '<Waters/left_vertices>: The provided polyline is not valid! polyline = {}'.format(polyline)
            self._left_vertices = polyline
        else:
            warnings.warn('<Waters/left_vertices>: left_vertices of waters are immutable!')

    @property
    def right_vertices(self) -> np.ndarray:
        """ Right vertices of the waters """
        return self._right_vertices

    @right_vertices.setter
    def right_vertices(self, polyline: np.ndarray):
        if self._right_vertices is None:
            assert is_valid_polyline(
                polyline), '<Waters/right_vertices>: The provided polyline is not valid! polyline = {}'.format(
                polyline)
            self._right_vertices = polyline
        else:
            warnings.warn('<Waters/right_vertices>: right_vertices of waters are immutable!')

    @property
    def center_vertices(self) -> np.ndarray:
        """ Center vertices of the waters """
        return self._center_vertices

    @center_vertices.setter
    def center_vertices(self, polyline: np.ndarray):
        if self._center_vertices is None:
            assert is_valid_polyline(
                polyline), '<Waters/center_vertices>: The provided polyline is not valid! polyline = {}'.format(
                polyline)
            self._center_vertices = polyline
        else:
            warnings.warn('<Waters/center_vertices>: center_vertices of water are immutable!')

    @property
    def predecessor(self) -> list:
        """ Predecessor of the waters """
        return self._predecessor

    @predecessor.setter
    def predecessor(self, predecessor: list):
        if self._predecessor is None:
            assert (is_list_of_natural_numbers(predecessor) and len(predecessor) >= 0), '<Waters/predecessor>: ' \
                                                                                        'Provided list ' \
                                                                                        'of predecessors is not valid!' \
                                                                                        'predecessors = {}'.format(
                predecessor)
            self._predecessor = predecessor
        else:
            warnings.warn(
                '<Waters/predecessor>: predecessor of waters is immutable!')

    @property
    def successor(self) -> list:
        """ Successor of the waters """
        return self._successor

    @successor.setter
    def successor(self, successor: list):
        if self._successor is None:
            assert (is_list_of_natural_numbers(successor) and len(successor) >= 0), '<Waters/predecessor>: Provided ' \
                                                                                    'list of successors is not valid!' \
                                                                                    'successors = {}'.format(successor)
            self._successor = successor
        else:
            warnings.warn(
                '<Waters/successor>: successor of water is immutable!')

    @waters_type.setter
    def waters_type(self, waters_type: Set[WatersType]):
        if self._waters_type is None or len(self._waters_type) == 0:
            assert isinstance(waters_type, set) and all(isinstance(elem, WatersType) for elem in waters_type), \
                '<Waters/waters_type>: ''Provided type is not valid! type = {}'.format(type(waters_type))
            self._waters_type = waters_type
        else:
            warnings.warn(
                '<Water/waters_type>: type of water is immutable!')

    @property
    def traffic_signs(self) -> Set[int]:
        """ Traffic signs of the waters """
        return self._traffic_signs

    @traffic_signs.setter
    def traffic_signs(self, traffic_sign_ids: Set[int]):
        if self._traffic_signs is None:
            assert isinstance(traffic_sign_ids, set), \
                '<Waters/traffic_signs>: provided list of ids is not a ' \
                'set! type = {}'.format(type(traffic_sign_ids))
            self._traffic_signs = traffic_sign_ids
        else:
            warnings.warn(
                '<Waters/traffic_signs>: traffic_signs of water is immutable!')

    @property
    def depth(self):
        """ Depth of the waters """
        return self._depth

    @depth.setter
    def depth(self, depth: float):
        assert isinstance(depth, float), \
            '<Waters/depth>: argument depth of wrong ' \
            'type. Expected type: %s. Got type: %s.' \
            % (float, type(depth))
        assert depth >= 0, '<Waters/depth>: argument depth is a negative number. ' \
                           'Expected type %s is a positive number. Got: %s.' \
                           % (float, depth)
        self._depth = depth

    def translate_rotate(self, translation: np.ndarray, angle: float):
        """
        This method translates and rotates a water

        :param translation: The translation given as [x_off,y_off] for the x and y translation
        :param angle: The rotation angle in radian (counter-clockwise defined)
        """

        assert is_real_number_vector(translation,
                                     2), '<Waters/translate_rotate>: provided translation ' \
                                         'is not valid! translation = {}'.format(translation)
        assert is_valid_orientation(
            angle), '<Waters/translate_rotate>: provided angle is not valid! angle = {}'.format(angle)

        t_m = translation_rotation_matrix(translation,angle)
        tmp = t_m.dot(np.vstack((self.center_vertices.transpose(),
                                 np.ones((1, self.center_vertices.shape[0])))))
        tmp = tmp[0:2, :]
        self._center_vertices = tmp.transpose()

        tmp = t_m.dot(np.vstack((self.left_vertices.transpose(),
                                 np.ones((1, self.left_vertices.shape[0])))))
        tmp = tmp[0:2, :]
        self._left_vertices = tmp.transpose()

        tmp = t_m.dot(np.vstack((self.right_vertices.transpose(),
                                 np.ones((1, self.right_vertices.shape[0])))))
        tmp = tmp[0:2, :]
        self._right_vertices = tmp.transpose()

        if self._polygon is not None:
            self._polygon = None
            self._polygon = self.convert_to_polygon()

    def convert_to_polygon(self) -> Polygon:
        """
        Converts the given water to a polygon representation

        :return: The polygon of the water
        """
        if self._polygon is None:
            self._polygon = Polygon(np.concatenate((self.right_vertices,
                                                    np.flip(self.left_vertices, 0))))
        return self._polygon

    def contains_points(self, point_list: np.ndarray) -> List[bool]:
        """
        Checks if a list of points is enclosed in the water

        :param point_list: The list of points in the form [[px1,py1],[px2,py2,],...]
        :return: List of bools with True indicating point is enclosed and False otherwise
        """
        assert isinstance(point_list,
                          ValidTypes.ARRAY), '<Waters/contains_points>: provided list of points is not a list! type ' \
                                             '= {}'.format(type(point_list))
        assert is_valid_polyline(
            point_list), 'Waters/contains_points>: provided list of points is malformed! points = {}'.format(
            point_list)

        res = list()

        poly = self.convert_to_polygon()
        for p in point_list:
            res.append(poly.contains_point(p))

        return res

    def get_obstacles(self, obstacles: List[Obstacle], time_step: int = 0) -> List[Obstacle]:
        """
        Returns the subset of obstacles,  which are located in the water, of a given candidate set

        :param obstacles: The set of obstacle candidates
        :param time_step: The time step for the occupancy to check
        :return: The subset of obstacles which are located in the water
        """

        assert isinstance(obstacles, list) and all(isinstance(o, Obstacle) for o in
                                                   obstacles), '<Waters/get_obstacles>: Provided list of obstacles' \
                                                               ' is malformed! obstacles = {}'.format(
            obstacles)

        res = list()

        for o in obstacles:
            o_shape = o.occupancy_at_time(time_step).shape

            vertices = list()

            if isinstance(o_shape, ShapeGroup):
                for sh in o_shape.shapes:
                    if isinstance(sh, Circle):
                        vertices.append(sh.center)
                    else:
                        vertices.append(sh.vertices)
                        vertices = np.append(vertices, [o_shape.center], axis=0)
            else:
                if isinstance(o_shape, Circle):
                    vertices = o_shape.center
                else:
                    vertices = o_shape.vertices
                    vertices = np.append(vertices, [o_shape.center], axis=0)

            if any(self.contains_points(np.array(vertices))):
                res.append(o)

        return res

    def add_traffic_sign_to_water(self, traffic_sign_id: int):
        """
        Adds a traffic sign ID to water

        :param traffic_sign_id: traffic sign ID to add
        """
        self.traffic_signs.add(traffic_sign_id)

class Shallow(Waters):
    """Class to describe a shallow with a defined shape and depth"""

    def __init__(self, shape: Shape,  waters_id: int, depth: float = 10.0):
        """
        :param shape: shape of the shallow
        :param waters_id: id of the shallow
        :param depth: depth of the shallow in meters (default: 10.0)
        """

        self._shape = shape
        self._depth = depth
        self._waters_id = waters_id
        self._waters_type = WatersType.SHALLOW

    def __str__(self):
        shallow_str = "\n"
        shallow_str += "Shallow:\n"
        shallow_str += "- Shape: {}\n".format(type(self._shape).__name__)
        shallow_str += "- Center-Position: {}\n".format(str(self.shape.center))
        shallow_str += "- Depth: {} Meters\n".format(str(self.depth))
        return shallow_str
        
    def __repr__(self):
        return f"Shallow(shape={type(self._shape).__name__}, " \
               f"waters_id={str(self.waters_id)}, " \
               f"center_position={str(self.shape.center)}, " \
               f"depth={str(self.depth)}"

    @property
    def waters_type(self) -> WatersType:
        """ Type of the waters """
        return self._waters_type

    @property
    def waters_id(self) -> int:
        """ ID of the waters """
        return self._waters_id

    @waters_id.setter
    def waters_id(self, f_id: int):
        if self._waters_id is None:
            assert is_natural_number(f_id), '<Waters/waters_id>: Provided waters_id is not valid! id={}'.format(f_id)
            self._waters_id = f_id
        else:
            warnings.warn('<Waters/waters_id>: waters_id of waters is immutable')

    @property
    def shape(self):
        """ Shape of the shallow """
        return self._shape

    @shape.setter
    def shape(self, shape: Shape):
        assert isinstance(shape, Shape), \
            '<Shallow/shape>: argument shape of wrong ' \
            'type. Expected type: %s. Got type: %s.' \
            % (Shape, type(shape))
        self._shape = shape

    @property
    def depth(self):
        """ Depth of the shallow """
        return self._depth

    @depth.setter
    def depth(self, depth: float):
        assert isinstance(depth, float), \
            '<Shallow/depth>: argument depth of wrong ' \
            'type. Expected type: %s. Got type: %s.' \
            % (float, type(depth))
        assert depth >= 0, '<Shallow/depth>: argument depth is a negative number. ' \
                           'Expected type %s is a positive number. Got: %s.' \
                           % (float, depth)
        self._depth = depth

    def translate_rotate(self, translation: np.ndarray, angle: float):
        """ Translates and rotates the shallow """
        new_shape = self.shape.translate_rotate(translation,angle)
        self.shape = new_shape

    def contains_points(self, point_list: np.ndarray)-> List[bool]:
        """
        Checks if a list of points is enclosed in the shallow

        :param point_list: The list of points in the form [[px1,py1],[px2,py2,],...]
        :return: List of bools with True indicating point is enclosed and False otherwise
        """
        
        assert isinstance(point_list,
                          ValidTypes.ARRAY), '<Shallow/contains_points>: provided list of points is not a list! type ' \
                                             '= {}'.format(type(point_list))
        res = list()

        for p in point_list:
            res.append(self.shape.contains_point(p))

        return res

    def get_obstacles(self, obstacles: List[Obstacle], time_step: int = 0) -> List[Obstacle]:
        """
        Returns the subset of obstacles,  which are located in the water,  of a given candidate set

        :param obstacles: The set of obstacle candidates
        :param time_step: The time step for the occupancy to check
        :return: The subset of obstacles which are located in the water
        """

        assert isinstance(obstacles, list) and all(isinstance(o, Obstacle) for o in
                                                   obstacles), '<Shallow/get_obstacles>: Provided list of obstacles' \
                                                               ' is malformed! obstacles = {}'.format(
            obstacles)

        res = list()

        for o in obstacles:
            o_shape = o.occupancy_at_time(time_step).shape

            vertices = list()

            if isinstance(o_shape, ShapeGroup):
                for sh in o_shape.shapes:
                    if isinstance(sh, Circle):
                        vertices.append(sh.center)
                    else:
                        vertices.append(sh.vertices)
                        vertices = np.append(vertices, [o_shape.center], axis=0)
            else:
                if isinstance(o_shape, Circle):
                    vertices = o_shape.center
                else:
                    vertices = o_shape.vertices
                    vertices = np.append(vertices, [o_shape.center], axis=0)

            if any(self.contains_points(np.array(vertices))):
                res.append(o)

        return res

class WatersNetwork(IDrawable):
    """
    Class which represents a network of connected waters (waterways and shallows)
    """

    def __init__(self, center_nav_area: np.ndarray, length_nav_area: float, width_nav_area: float, orientation_nav_area: float):
        self._waterways: Dict[int, Waterway] = {}
        self._shallows: Dict[int, Shallow] = {}
        self._traffic_signs: Dict[int, TrafficSign] = {}
        self._unassigned_traffic_signs: Dict[int, TrafficSign] = {} 
        
        assert len(
            center_nav_area) == 2, '<Watersnetwork/center navigationable area> Error: dimensions do not fit. Got { } but 2 is expected'.format(
            len(center_nav_area))
        assert length_nav_area >= 0, '<Watersnetwork/length navigationable area> Error: negative length not allowed'
        assert width_nav_area >= 0, '<Watersnetwork/width navigationable area> Error: negative width not allowed'
        assert is_valid_orientation(
            orientation_nav_area), '<WatersNetwork/orientation navigationable area>: provided orientation is not valid! orientation = {}'.format(orientation_nav_area)

        self._navigationable_area = Rectangle(length_nav_area,width_nav_area,center_nav_area,orientation_nav_area)


    def __eq__(self, other):
        if not isinstance(other, WatersNetwork):
            warnings.warn(f"Inequality between WatersNetwork {repr(self)} and different type {type(other)}")
            return False

        list_elements_eq = True
        waters_network_eq = True
        elements = [self._waterways, self._traffic_signs, self._shallows]
        elements_other = [other._waterways, other._traffic_signs, other._shallows]
        for i in range(0, len(elements)):
            e = elements[i]
            e_other = elements_other[i]
            waters_network_eq = waters_network_eq and len(e) == len(e_other)
            for k in e.keys():
                if k not in e_other:
                    waters_network_eq = False
                    continue
                if e.get(k) != e_other.get(k):
                    list_elements_eq = False

        if not waters_network_eq:
            warnings.warn(f"Inequality of WatersNetwork {repr(self)} and the other one {repr(other)}")

        return waters_network_eq and list_elements_eq

    def __hash__(self):
        return hash((frozenset(self._waterways.items()),
                     frozenset(self._shallows.items()),
                     frozenset(self._traffic_signs.items())))

    def __str__(self):
        return f"WatersNetwork consists of waterways {set(self._waterways.keys())}, " \
               f" shallows {set(self._shallows.keys())}, " \
               f" and traffic signs {set(self._traffic_signs.keys())}"

    def __repr__(self):
        return f"WatersNetwork(waterways={repr(self._waterways)}, shallows={repr(self._shallows)}, traffic_signs={repr(self._traffic_signs)}" 

    @property
    def navigationable_area(self) -> Rectangle:
        """ Navigationable area of the network """
        return self._navigationable_area

    @navigationable_area.setter
    def navigationable_area(self, navigationable_area: Rectangle):
        warnings.warn('<WatersNetwork/navigationable area>: navigationable area of network are immutable')

    @property
    def waters(self) -> List[Waters]:
        """ Waters of the network """
        return list(self._waterways.values()) + list(self._shallows.values())

    @property
    def waterways(self) -> List[Waters]:
        """ Waterways of the network """
        return list(self._waterways.values())

    @property
    def shallows(self) -> List[Waters]:
        """ Shallows of the network """
        return list(self._shallows.values())

    @waters.setter
    def waters(self, waters: list):
        warnings.warn('<WatersNetwork/waters>: waters of network are immutable')

    @waterways.setter
    def waterways(self, waters: list):
        warnings.warn('<WatersNetwork/waterways>: waterways of network are immutable')

    @shallows.setter
    def shallows(self, waters: list):
        warnings.warn('<WatersNetwork/shallows>: shallows of network are immutable')

    @property
    def traffic_signs(self) -> List[TrafficSign]:
        """ Traffic signs of the network """
        return list(self._traffic_signs.values())

    def find_waters_by_id(self, waters_id: int) -> Waters:
        """
        Finds a water (shallow or waterway) for a given waters_id

        :param waters_id: The id of the waterway to find
        :return: The waters object if the id exists and None otherwise
        """

        assert is_natural_number(
            waters_id), '<WatersNetwork/find_waters_by_id>: provided id is not valid! id = {}'.format(waters_id)

        res = self.find_waterway_by_id(waters_id)
        if res is None:
            return self.find_shallow_by_id(waters_id)
        else:
            return res
        
    def find_waterway_by_id(self, waters_id: int) -> Waters:
        """
        Finds a waterway for a given waters_id

        :param waters_id: The id of the waterway to find
        :return: The waterway object if the id exists and None otherwise
        """
        assert is_natural_number(
            waters_id), '<WatersNetwork/find_waterway_by_id>: provided id is not valid! id = {}'.format(waters_id)

        return self._waterways[waters_id] if waters_id in self._waterways else None

    def find_shallow_by_id(self, waters_id: int) -> Waters:
        """
        Finds a shallow for a given waters_id

        :param waters_id: The id of the shallow to find
        :return: The shallow object if the id exists and None otherwise
        """
        assert is_natural_number(
            waters_id), '<WatersNetwork/find_shallow_by_id>: provided id is not valid! id = {}'.format(waters_id)

        return self._shallows[waters_id] if waters_id in self._shallows else None

    def find_traffic_sign_by_id(self, traffic_sign_id: int) -> TrafficSign:
        """
        Finds a traffic sign for a given traffic_sign_id

        :param traffic_sign_id: The id of the traffic sign to find
        :return: The traffic sign object if the id exists and None otherwise
        """
        assert is_natural_number(
            traffic_sign_id), '<WatersNetwork/find_traffic_sign_by_id>: provided id is not valid! ' \
                              'id = {}'.format(traffic_sign_id)

        return self._traffic_signs[traffic_sign_id] if traffic_sign_id in self._traffic_signs else None

    def add_waters(self, water: Waters):
        """
        Adds a waters (shallow and waterway) to the WatersNetwork

        :param water: The waters to add
        :return: True if the waters has successfully been added to the network, false otherwise
        """

        assert isinstance(water, Waters), '<WatersNetwork/add_waters>: provided water is not of ' \
                                             'type water! type = {}'.format(type(water))
        if isinstance(water, Shallow):
            if water.waters_id in self._shallows.keys():
                warnings.warn('Shallow already exists in network! No changes are made.')
                return False
            else:
                self._shallows[water.waters_id] = water
                return True
        elif isinstance(water, Waterway):
            if water.waters_id in self._waterways.keys():
                warnings.warn('Waters already exists in network! No changes are made.')
                return False
            else:
                self._waterways[water.waters_id] = water
                return True

    def add_traffic_sign(self, traffic_sign: TrafficSign, waters_ids: Union[None, Set[int]] = None):
        """
        Adds a traffic sign to the WatersNetwork

        :param traffic_sign: The traffic sign to add
        :param waters_ids: Waters the traffic sign should be referenced from
        :return: True if the traffic sign has successfully been added to the network, false otherwise
        """

        assert isinstance(traffic_sign, TrafficSign), '<WatersNetwork/add_traffic_sign>: provided traffic sign is ' \
                                                      'not of type traffic_sign! type = {}'.format(type(traffic_sign))

        if traffic_sign.traffic_sign_id in self._traffic_signs.keys():
            warnings.warn('Traffic sign with ID {} already exists in network! '
                          'No changes are made.'.format(traffic_sign.traffic_sign_id))
            return False
        else:
            self._traffic_signs[traffic_sign.traffic_sign_id] = traffic_sign
            if waters_ids is None or len(waters_ids) < 1:
                warnings.warn('Traffic sign was not referenced to water, use post_assign_traffic_sign to assign it later.')
                self._unassigned_traffic_signs[traffic_sign.traffic_sign_id] = traffic_sign
            else:
                for water_id in waters_ids:
                    if water_id is not None:
                        water = self.find_waterway_by_id(water_id)
                        if water is not None:
                            water.add_traffic_sign_to_water(traffic_sign.traffic_sign_id)
                        else:
                            warnings.warn('Traffic sign cannot be referenced to water because the water does not exist.')
                    else:
                        pass
            return True
    
    def post_assign_traffic_sign(self, traffic_sign_id: int, waters_ids: Set[int]):
        """
        Assign an unassigned traffic sign to the WatersNetwork

        :param traffic_sign_id: The traffic sign id to be assigned
        :param waters_ids: Waters the traffic sign should be referenced from
        :return: True if the traffic sign has successfully been added to the network, false otherwise
        """

        if traffic_sign_id not in self._traffic_signs.keys():
            warnings.warn('Traffic sign with ID {} does not exist in network! '
                          'No changes are made.'.format(traffic_sign_id))
            return False

        elif traffic_sign_id  not in self._unassigned_traffic_signs.keys():
            warnings.warn('Traffic sign with ID {} is already assigned to a Water in network! '
                          'No changes are made.'.format(traffic_sign_id))
            return False

        else:
            assigned = False
            for water_id in waters_ids:
                water = self.find_waterway_by_id(water_id)
                if water is not None:
                    water.add_traffic_sign_to_water(traffic_sign_id)
                    assigned = True
                else:
                    warnings.warn('Traffic sign cannot be referenced to water because the water does not exist.')
            if assigned:
                del self._unassigned_traffic_signs[traffic_sign_id]
            return True

    def add_waters_from_network(self, waters_network: 'WatersNetwork'):
        """
        Adds waters from a given network object to the current network

        :param waters_network: The water network
        :return: True if all waters have been added to the network, false otherwise
        """
        flag = True

        for f in waters_network.waters:
            flag = flag and self.add_waters(f)

        return flag

    def remove_waters(self, waters_id: int):
        """
        Removes waters from a waters network and deletes all references.

        :param waters_id: ID of waters which should be removed.
        """
        if waters_id in self._waterways.keys():
            del self._waterways[waters_id]
        if waters_id in self._shallows.keys():
            del self._shallows[waters_id]

    def remove_traffic_sign(self, traffic_sign_id: int):
        """
        Removes a traffic sign from a waters network and deletes all references.

        :param traffic_sign_id: ID of traffic sign which should be removed.
        """
        if traffic_sign_id in self._traffic_signs.keys():
            del self._traffic_signs[traffic_sign_id]

    def translate_rotate(self, translation: np.ndarray, angle: float):
        """
        Translates and rotates the complete waters network

        :param translation: The translation given as [x_off,y_off] for the x and y translation
        :param angle: The rotation angle in radian (counter-clockwise defined)
        """

        assert is_real_number_vector(translation,
                                     2), '<WatersNetwork/translate_rotate>: provided translation is not valid! ' \
                                         'translation = {}'.format(translation)
        assert is_valid_orientation(
            angle), '<WatersNetwork/translate_rotate>: provided angle is not valid! angle = {}'.format(angle)

        nav_area_new = self._navigationable_area.translate_rotate(translation,angle)
        self._navigationable_area = nav_area_new
        for waterway in self._waterways.values():
            waterway.translate_rotate(translation, angle)
        for shallow in self._shallows.values():
            shallow.translate_rotate(translation, angle)
        for traffic_sign in self._traffic_signs.values():
            traffic_sign.translate_rotate(translation, angle)

    def find_waterway_by_position(self, point_list: List[np.ndarray]) -> List[List[int]]:
        """
        Finds the waterway id of a given position

        :param point_list: The list of positions to check
        :return: A list of water ids. If the position could not be matched to a water, an empty list is returned
        """
        assert isinstance(point_list,
                          ValidTypes.LISTS), '<waterways/contains_points>: provided list of points is not a list! ' \
                                             'type = {}'.format(type(point_list))

        res = list()

        polygons = [(f.waters_id, f.convert_to_polygon()) for f in self.waterways]

        for point in point_list:
            mapped = list()
            for waters_id, poly in polygons:
                if poly.contains_point(point):
                    mapped.append(waters_id)
            res.append(mapped)

        return res

    def find_waterway_by_shape(self, shape: Shape) -> List[int]:
        """
        Finds the waterway id of a given shape

        :param shape: The shape to check
        :return: A list of water ids. If the position could not be matched to a water, an empty list is returned
        """
        assert isinstance(shape, (Circle, Polygon, Rectangle)), '<Waters/find_water_by_shape>: ' \
                                                                'provided shape is not a shape! ' \
                                                                'type = {}'.format(type(shape))

        res = []

        polygons = [(l.waters_id, l.convert_to_polygon()) for l in self.waterways]

        for waters_id, poly in polygons:
            if poly.shapely_object.intersects(shape.shapely_object):
                res.append(waters_id)

        return res

    def filter_obstacles_in_network(self, obstacles: List[Obstacle]) -> List[Obstacle]:
        """
        Returns the list of obstacles which are located in the water network

        :param obstacles: The list of obstacles to check
        :return: The list of obstacles which are located in the water network
        """

        res = list()

        map = self.map_obstacles_to_waters(obstacles)

        for k in map.keys():
            obs = map[k]
            for o in obs:
                if o not in res:
                    res.append(o)

        return res

    def map_obstacles_to_waters(self, obstacles: List[Obstacle]) -> Dict[int, List[Obstacle]]:
        """
        Maps a given list of obstacles to the waters of the water network

        :param obstacles: The list of CR obstacles
        :return: A dictionary with the water id as key and the list of obstacles on the water as a List[Obstacles]
        """
        mapping = {}

        for f in self.waters:
            mapped_objs = f.get_obstacles(obstacles)

            if len(mapped_objs) > 0:
                mapping[f.waters_id] = mapped_objs

        return mapping

    def waterways_in_proximity(self, point: list, radius: float) -> List[Waters]:
        """
        Finds all waterways which intersect a given circle, defined by the center point and radius

        :param point: The center of the circle
        :param radius: The radius of the circle
        :return: The list of waters which intersect the given circle
        """

        assert is_real_number_vector(point,
                                     length=2), '<WatersNetwork/waters_in_proximity>: provided point is ' \
                                                'not valid! point = {}'.format(point)
        assert is_positive(
            radius), '<WatersNetwork/waters_in_proximity>: provided radius is not valid! radius = {}'.format(radius)

        ids = self._waterways.keys()

        lanes = dict()

        rad_sqr = radius ** 2

        distance_list = list()

        for i in ids:

            if i not in lanes:
                water = self.find_waterway_by_id(i)

                distance = (water.center_vertices - point) ** 2.
                distance = distance[:, 0] + distance[:, 1]

                if any(np.greater_equal(rad_sqr, distance)):
                    lanes[i] = self.find_waterway_by_id(i)
                    distance_list.append(np.min(distance))

                index_minDist = np.argmin(distance - rad_sqr)

        indices = np.argsort(distance_list)
        water = list(lanes.values())

        return [water[i] for i in indices]

    def shallow_depth_for_positions(self, positions: List[np.ndarray]) -> List:
        """
        This function returns the shallow depth for positions

        :param positions: List of positions where each position is a 2D ndarray
        :return: List with the respective depths of the positions of the input list
        """

        depths = []
        for position in positions:
            is_infinite = True
            for shallow in self.shallows:
                if shallow.contains_points(np.array([position]))[0]:
                    depths.append(shallow.depth)
                    is_infinite = False
                    break
            if is_infinite:
                depths.append(np.inf)

        return depths

    def draw(self, renderer: IRenderer,
             draw_params: Union[ParamServer, dict, None] = None,
             call_stack: Optional[Tuple[str, ...]] = tuple()):
        renderer.draw_waters_network(self, draw_params, call_stack)

