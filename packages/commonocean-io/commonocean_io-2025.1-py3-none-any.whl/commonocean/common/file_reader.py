from xml.etree import ElementTree

import re

from commonocean.planning.goal import GoalRegion
from commonocean.planning.planning_problem import PlanningProblemSet, PlanningProblem
from commonocean.scenario.scenario import *
from commonocean.scenario.obstacle import *
from commonocean.scenario.traffic_sign import *
from commonocean.scenario.waters import Shallow, Waterway, WatersNetwork

from commonroad.common.util import AngleInterval
from commonroad.geometry.shape import *
from commonocean.scenario.trajectory import Trajectory
from commonocean.scenario.state import SpecificStateClasses
from commonroad.scenario.state import State, CustomState

# Tunneling from CR-IO #
from commonroad.common.reader.file_reader_xml import read_value_exact_or_interval as read_value_exact_or_interval_CR
from commonroad.common.reader.file_reader_xml import read_time as read_time_CR
from commonroad.common.reader.file_reader_xml import ShapeFactory, RectangleFactory, CircleFactory, PolygonFactory, PointFactory, PointListFactory
########################

__author__ = "Hanna Krasowski, Benedikt Pfleiderer, Fabian Thomas-Barein"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2023a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"

def read_value_exact_or_interval(xml_node: ElementTree.Element) \
        -> Union[float, Interval]:
    """
        :param xml_node: XML element
        :return: Interval
    """

    return read_value_exact_or_interval_CR(xml_node)


def read_time(xml_node: ElementTree.Element) -> Union[int, Interval]:
    """
        :param xml_node: XML element
        :return: Interval
    """

    return read_time_CR(xml_node)


class CommonOceanFileReader:
    """ Class which reads CommonOcean XML-files. The XML-files are composed of
    (1) a formal representation of the water network,
    (2) static and dynamic obstacles,
    (3) the planning problem of the ego vehicle(s). """

    def __init__(self, filename: str):
        """
        :param filename: full path + filename of the CommonOcean XML-file,
        """
        self._filename = filename
        self._tree = None
        self._dt = None
        self._benchmark_id = None
        self._meta_data = None

    def open(self) -> Tuple[Scenario, PlanningProblemSet]:
        """
        Reads a CommonOcean XML-file.

        :return: the scenario containing the water network and the obstacles and the planning problem set \
        containing the planning problems---initial states and goal regions--for all ego vessels.
        """
        self._read_header()
        scenario = self._open_scenario()
        planning_problem_set = self._open_planning_problem_set(scenario._waters_network)
        return scenario, planning_problem_set

    def open_waters_network(self) -> WatersNetwork:
        """
        Reads the water network of a CommonOcean XML-file.

        :return: object of class WatersNetwork
        """
        self._read_header()
        return WatersNetworkFactory.create_from_xml_node(self._tree)

    def _open_scenario(self) -> Scenario:
        """
        Reads the water network and obstacles from the CommonOcean XML-file.

        :return: object of class scenario containing the water network and the obstacles
        """
        scenario = ScenarioFactory.create_from_xml_node(self._tree, self._dt, self._benchmark_id,
                                                        self._commonocean_version, self._meta_data)
        return scenario

    def _open_planning_problem_set(self, waters_network: WatersNetwork) -> PlanningProblemSet:
        """
        Reads all planning problems from the CommonOcean XML-file.

        :return: object of class PlanningProblemSet containing the planning problems for all ego vessels.
        """
        planning_problem_set = PlanningProblemSetFactory.create_from_xml_node(self._tree, waters_network)
        return planning_problem_set

    def _read_header(self):
        """ Parses the CommonOcean XML-file into element tree; reads the global time step size of the time-discrete
        scenario and the CommonOcean benchmark ID."""
        self._parse_file()
        self._dt = self._get_dt()
        self._benchmark_id = self._get_benchmark_id()
        self._commonocean_version = self._get_commonocean_version()

        self._meta_data = {'author': self._get_author(),
                           'affiliation': self._get_affiliation(),
                           'source': self._get_source(),
                           'tags': self._get_tags(),
                           'location': Location()}

    def _parse_file(self):
        """ Parses the CommonOcean XML-file into element tree."""
        self._tree = ElementTree.parse(self._filename)

    def _get_dt(self) -> float:
        """ Reads the time step size of the time-discrete scenario."""
        return float(self._tree.getroot().get('timeStepSize'))

    def _get_benchmark_id(self) -> str:
        """ Reads the unique CommonOcean benchmark ID of the scenario."""
        return self._tree.getroot().get('benchmarkID')

    def _get_commonocean_version(self) -> str:
        """ Reads the CommonOcean version of the XML-file."""
        return self._tree.getroot().get('commonOceanVersion')

    def _get_author(self) -> str:
        """ Reads the author of the scenario."""
        return self._tree.getroot().get('author')

    def _get_affiliation(self) -> str:
        """ Reads the affiliation of the author of the scenario."""
        return self._tree.getroot().get('affiliation')

    def _get_source(self) -> str:
        """ Reads the source of the scenario."""
        return self._tree.getroot().get('source')

    def _get_tags(self) -> Set[Tag]:
        """ Reads the tags of the scenario."""
        tags_string = self._tree.getroot().get('tags')
        if tags_string is None:
            return None
        else:
            splits = tags_string.split()
            tags = set()
            for tag in splits:
                try:
                    tags.add(Tag(tag))
                except ValueError:
                    warnings.warn('Scenario tag \'{}\' not valid.'.format(tag), stacklevel=2)

            return tags


class ScenarioFactory:
    """ Class to create an object of class Scenario from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element, dt: float, benchmark_id: str, commonocean_version: str,
                             meta_data: dict):
        """
        :param xml_node: XML element
        :param dt: time step size of the scenario
        :param benchmark_id: unique CommonOcean benchmark ID
        :param commonocean_version: CommonOcean version of the file
        :return: CommonOcean scenario
        """
        meta_data["tags"] = TagsFactory.create_from_xml_node(xml_node)
        meta_data["location"] = LocationFactory.create_from_xml_node(xml_node)

        scenario_id = ScenarioID.from_benchmark_id(benchmark_id, commonocean_version)
        scenario = Scenario(dt, scenario_id, **meta_data)

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            scenario.add_objects(WatersNetworkFactory.create_from_xml_node(xml_node))

        scenario.add_objects(cls._obstacles(xml_node, scenario._waters_network))
        scenario.add_objects(cls._shallows(xml_node))

        return scenario

    @classmethod
    def _obstacles(cls, xml_node: ElementTree.Element, waters_network: WatersNetwork) -> List[Obstacle]:
        """
        Reads all obstacles specified in a CommonOcean XML-file.
        
        :param xml_node: XML element
        :param waters_network: WatersNetwork
        :return: list of static and dynamic obstacles specified in the CommonOcean XML-file
        """
        obstacles = []
        for o in xml_node.findall('staticObstacle'):
            obstacles.append(StaticObstacleFactory.create_from_xml_node(o, waters_network))
        for o in xml_node.findall('dynamicObstacle'):
            obstacles.append(DynamicObstacleFactory.create_from_xml_node(o, waters_network))
        return obstacles

    @classmethod
    def _shallows(cls, xml_node: ElementTree.Element) -> List[Shallow]:
        """
        Reads all shallows specified in a CommonOcean XML-file.

        :param xml_node: XML element
        :return: list of shallows specified in the CommonOcean XML-file
        """
        shallows = []
        for d in xml_node.findall('shallow'):
            shallows.append(ShallowFactory.create_from_xml_node(d))
        return shallows


class ShallowFactory:
    """ Class to create a shallow from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> Shallow:
        """
        :param xml_node: XML element
        :return: shallow
        """
        waters_id = int(xml_node.get('id'))
        shape = ShapeFactory.create_from_xml_node(xml_node.find('shape'))
        if xml_node.find('depth') is None:
            return Shallow(shape)
        else:
            depth = float(xml_node.find('depth').find('exact').text)
            return Shallow(shape, waters_id, depth)


class TagsFactory:
    """ Class to create a tag set from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> Set[Tag]:
        """
        :param xml_node: XML element
        :return: set of tags
        """
        tags = set()
        tag_element = xml_node.find('scenarioTags')
        if tag_element is not None:
            for elem in Tag:
                if tag_element.find(elem.value) is not None:
                    tags.add(elem)
            return tags
        else:
            return None


class LocationFactory:
    """ Class to create a location from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> Union[Location, None]:
        """
        :param xml_node: XML element
        :return: location object
        """
        if xml_node.find('location') is not None:
            location_element = xml_node.find('location')
            geo_name_id = int(location_element.find('geoNameId').text)
            gps_latitude = float(location_element.find('gpsLatitude').text)
            gps_longitude = float(location_element.find('gpsLongitude').text)
            if location_element.find('geoTransformation') is not None:
                geo_transformation = GeoTransformationFactory.create_from_xml_node(
                    location_element.find('geoTransformation'))
            else:
                geo_transformation = None
            if location_element.find('environment') is not None:
                environment = EnvironmentFactory.create_from_xml_node(
                    location_element.find('environment'))
            else:
                environment = None

            return Location(geo_name_id, gps_latitude, gps_longitude, geo_transformation, environment)
        else:
            return None


class GeoTransformationFactory:
    """ Class to create a geotransformation object of an XML element according to the CommonOcean specification."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> GeoTransformation:
        """
        :param xml_node: XML element
        :return: GeoTransformation object
        """
        geo_reference = xml_node.find('geoReference').text
        x_translation = float(xml_node.find('xTranslation').text)
        y_translation = float(xml_node.find('yTranslation').text)
        z_rotation = float(xml_node.find('zRotation').text)
        scaling = float(xml_node.find('scaling').text)

        return GeoTransformation(geo_reference, x_translation, y_translation, z_rotation, scaling)


class EnvironmentFactory:
    """ Class to create a environment object of an XML element according to the CommonOcean specification."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> Environment:
        """
        :param xml_node: XML element
        :return: Environment object
        """
        time = TimeFactory.create_from_xml_node(xml_node.find('time').text)
        weather = Weather(xml_node.find('weather').text)
        sea_state = SeaState(xml_node.find('seaState').text)
        time_of_day = TimeOfDay(xml_node.find('timeOfDay').text)

        return Environment(time, time_of_day, weather, sea_state)


class TimeFactory:
    """ Class to create a time object of an XML element."""

    @classmethod
    def create_from_xml_node(cls, time_text: str) -> Time:
        """
        :param time_text: time as string
        :return: time object
        """
        year = int(time_text[0:4])
        month = int(time_text[5:7])
        day = int(time_text[8:10])
        hours = int(time_text[11:13])
        minutes = int(time_text[14:16])

        return Time(year, month, day, hours, minutes)


class WatersNetworkFactory:
    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> WatersNetwork:
        """
        Reads all waters specified in a CommonOcean XML-file.
        :param xml_node: XML element
        :return: list of waters
        """
        shape = StaticObstacleFactory.read_shape(xml_node.find('navigationableArea'))
        waters_network = WatersNetwork(shape.center, shape.length, shape.width, shape.orientation)
        waters = []
        assigned_traffic_signs = []
        for waters_node in xml_node.findall('waterway'):
            waters.append(WaterwayFactory.create_from_xml_node(waters_node))
            for traffic_sign_ref in waters_node.findall('trafficSignRef'):
                    if traffic_sign_ref.get("ref") is not None:
                        assigned_traffic_signs.append(int(traffic_sign_ref.get("ref")))
                    else:
                        raise ValueError('<WatersNetworkFactory/create_from_xml_node>: Unknown type of traffic sign reference: %s.'
                                        % traffic_sign_ref.get("ref"))
            
        for water in waters:
            waters_network.add_waters(water)

        for traffic_sign_node in xml_node.findall('trafficSign'):
            unassigned = True
            if int(traffic_sign_node.get('id')) in assigned_traffic_signs:
                waters_network.add_traffic_sign(TrafficSignFactory.create_from_xml_node(traffic_sign_node), [None, None])
            else:
                waters_network.add_traffic_sign(TrafficSignFactory.create_from_xml_node(traffic_sign_node), [])

        return waters_network


class WaterwayFactory:
    """ Class to create an object of class Waters from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> Waters:
        """
        :param xml_node: XML element
        :return: object of class Waterway according to the CommonOcean specification.
        """
        waters_id = int(xml_node.get('id'))

        left_vertices = cls._vertices(xml_node.find('leftBound'))
        right_vertices = cls._vertices(xml_node.find('rightBound'))
        center_vertices = 0.5 * (left_vertices + right_vertices)
        # center_vertices = right_vertices

        predecessors = cls._predecessors(xml_node)
        successors = cls._successors(xml_node)

        waters_type = cls._waters_type(xml_node)

        traffic_signs = cls._traffic_signs(xml_node)

        if xml_node.find('depth') is not None:
            depth = float(xml_node.find('depth').find('exact').text)
        else:
            depth = np.inf

        return Waterway(
            left_vertices=left_vertices, center_vertices=center_vertices, right_vertices=right_vertices,
            waters_id=waters_id,
            waters_type=waters_type,
            predecessor=predecessors, successor=successors,
            traffic_signs=traffic_signs,
            depth=depth)

    @classmethod
    def _vertices(cls, xml_node: ElementTree.Element) -> np.ndarray:
        """
        Reads the vertices of the water boundary.
        :param xml_node: XML element
        :return: The vertices of the boundary of the Waterway described as a polyline
        """
        return PointListFactory.create_from_xml_node(xml_node)

    @classmethod
    def _predecessors(cls, xml_node: ElementTree.Element) -> List[int]:
        """
        Reads all predecessor waters.
        :param xml_node: XML element
        :return: list of IDs of all predecessor waters
        """
        predecessors = list()
        for l in xml_node.findall('predecessor'):
            predecessors.append(int(l.get('ref')))
        return predecessors

    @classmethod
    def _successors(cls, xml_node: ElementTree.Element) -> List[int]:
        """
        Reads all successor waters.
        :param xml_node: XML element
        :return: list of IDs of all successor waters
        """
        successors = list()
        for l in xml_node.findall('successor'):
            successors.append(int(l.get('ref')))
        return successors

    @classmethod
    def _waters_type(cls, xml_node: ElementTree.Element) -> WatersType:
        """
        Reads the water types of the water.

        :param xml_node: XML element
        :return: set of water types for a water
        """

        for f_type in xml_node.findall('watersType'):
            if WatersType(f_type.text) is not None:
                waters_type = (WatersType(f_type.text))
            else:
                raise ValueError('<WaterwayFactory/_waters_type>: Unkown type of water: %s.' % f_type.text)
        return waters_type

    @classmethod
    def _traffic_signs(cls, xml_node: ElementTree.Element) -> Union[Set[int], None]:
        """
        Reads the traffic sign references of the water.

        :param xml_node: XML element
        :return: set of traffic sign IDs (None if not specified).
        """
        traffic_signs = set()
        for traffic_sign_ref in xml_node.findall('trafficSignRef'):
            if traffic_sign_ref.get("ref") is not None:
                traffic_signs.add(int(traffic_sign_ref.get("ref")))
            else:
                raise ValueError('<WaterwayFactory/_traffic_signs>: Unknown type of traffic sign reference: %s.'
                                 % traffic_sign_ref.get("ref"))
        return traffic_signs



class TrafficSignFactory:
    """ Class to create an object of class TrafficSign from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> TrafficSign:
        """
        :param xml_node: XML element
        :param first_traffic_sign_occurence: set of first occurences of traffic sign
        :param waters_network: CommonOcean waters network
        :return: object of class TrafficSign according to the CommonOcean specification.
        """
        traffic_sign_id = int(xml_node.get('id'))

        traffic_sign_elements = []
        for element in xml_node.findall('trafficSignElement'):
            traffic_sign_elements.append(TrafficSignElementFactory.create_from_xml_node(element))

        if xml_node.find('position') is not None:
            position = PointFactory.create_from_xml_node(xml_node.find('position').find('point'))

        if xml_node.get('virtual') is not None:
            if xml_node.get('virtual').text == "true":
                virtual = True
            elif xml_node.get('virtual').text == "false":
                virtual = False
            else:
                raise ValueError()
        else:
            virtual = False

        related_obstacle_ref = xml_node.find('relatedObstacleRef')
        if related_obstacle_ref is not None:
            related_obstacle = int(related_obstacle_ref.get("ref"))
        else:
            related_obstacle = None

        return TrafficSign(traffic_sign_id=traffic_sign_id, position=position,
                           traffic_sign_elements=traffic_sign_elements, virtual=virtual, related_obstacle=related_obstacle)


class TrafficSignElementFactory:
    """ Class to create an object of class TrafficSignElement from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> TrafficSignElement:
        """
        :param xml_node: XML element
        :return: object of class TrafficSignElement according to the CommonOcean specification.
        """

        traffic_sign_element_id = TrafficSignElementID(xml_node.find('trafficSignID').text)

        additional_values = []
        for additional_value in xml_node.findall('additionalValue'):
            additional_values.append(additional_value.text)

        return TrafficSignElement(traffic_sign_element_id=traffic_sign_element_id,
                                  additional_values=additional_values)

class ObstacleFactory(ABC):
    """ Class to create an Obstacle from an XML element."""

    @classmethod
    def read_type(cls, xml_node: ElementTree.Element) -> ObstacleType:
        """
        :param xml_node: XML element
        :return: object of class ObstacleType according to the CommonOcean specification.
        """

        obstacle_type = None
        if xml_node.find('type') is not None:
            if ObstacleType(xml_node.find('type').text) is not None:
                obstacle_type = ObstacleType(xml_node.find('type').text)
            else:
                raise ValueError('Type of obstacle is unknown. Got type: {}'.format(xml_node.find('type').text))

        return obstacle_type

    @classmethod
    def read_id(cls, xml_node: ElementTree.Element) -> int:
        """
        :param xml_node: XML element
        :return: int.
        """

        obstacle_id = int(xml_node.get('id'))
        return obstacle_id

    @classmethod
    def read_depth(cls, xml_node: ElementTree.Element) -> Union[None, float]:
        """
        :param xml_node: XML element
        :return: int.
        """

        if xml_node.find('depth') is None:
            return None
        else:
            depth_text = xml_node.find('depth').text
            if depth_text != "inf":
                depth = float(depth_text)
            else:
                depth = np.inf
        return depth

    @classmethod
    def read_initial_state(cls, xml_node: ElementTree.Element) -> State:
        """
        :param xml_node: XML element
        :return: object of class CustomState according to the CommonRoad specification.
        """

        initial_state = StateFactory.create_from_xml_node(xml_node)
        return initial_state

    @classmethod
    def read_shape(cls, xml_node: ElementTree.Element) -> Shape:
        """
        :param xml_node: XML element
        :return: object of class Shape.
        """

        shape = ShapeFactory.create_from_xml_node(xml_node)
        return shape


class StaticObstacleFactory(ObstacleFactory):
    """ Class to create a Static Obstacle from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element, waters_network: WatersNetwork) -> StaticObstacle:
        """
        :param xml_node: XML element
        :param xml_node: waters network element
        :return: object of class StaticObstacle according to the CommonOcean specification.
        """

        obstacle_type = StaticObstacleFactory.read_type(xml_node)
        obstacle_id = StaticObstacleFactory.read_id(xml_node)
        initial_state = StaticObstacleFactory.read_initial_state(xml_node.find('initialState'))
        shape = StaticObstacleFactory.read_shape(xml_node.find('shape'))
        depth = StaticObstacleFactory.read_depth(xml_node)

        return StaticObstacle(obstacle_id=obstacle_id, obstacle_type=obstacle_type,
                              obstacle_shape=shape, initial_state=initial_state, depth = depth)


class DynamicObstacleFactory(ObstacleFactory):
    """ Class to create a Dynamic Obstacle from an XML element."""

    @staticmethod
    def find_obstacle_shape_lanelets(initial_state: State, state_list: List[State], waters_network: WatersNetwork,
                                     obstacle_id: int, shape: Shape) -> Dict[int, Set[int]]:
        """
        Extracts for each shape the corresponding waters it is on

        :param initial_state: initial CommonOcean state
        :param state_list: trajectory state list
        :param waters_network: CommonOcean water network
        :param obstacle_id: ID of obstacle
        :param shape: shape of obstacle
        :return: list of IDs of all predecessor waters
        """
        compl_state_list = [initial_state] + state_list
        lanelet_ids_per_state = {}

        for state in compl_state_list:
            rotated_shape = shape.rotate_translate_local(state.position, state.orientation)
            lanelet_ids = waters_network.find_water_by_shape(rotated_shape)
            for l_id in lanelet_ids:
                waters_network.find_lanelet_by_id(l_id).add_dynamic_obstacle_to_lanelet(obstacle_id=obstacle_id,
                                                                                        time_step=state.time_step)
            lanelet_ids_per_state[state.time_step] = set(lanelet_ids)

        return lanelet_ids_per_state

    @staticmethod
    def find_obstacle_center_lanelets(initial_state: State, state_list: List[State],
                                      waters_network: WatersNetwork) -> Dict[int, Set[int]]:
        """
        Extracts for each shape the corresponding waters it is on

        :param initial_state: initial CommonOcean state
        :param state_list: trajectory state list
        :param waters_network: CommonOcean water network
        :return: list of IDs of all predecessor waters
        """
        compl_state_list = [initial_state] + state_list
        lanelet_ids_per_state = {}

        for state in compl_state_list:
            lanelet_ids = waters_network.find_lanelet_by_position([state.position])[0]
            lanelet_ids_per_state[state.time_step] = set(lanelet_ids)

        return lanelet_ids_per_state

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element, waters_network: WatersNetwork) -> DynamicObstacle:
        """
        :param xml_node: XML element
        :param xml_node: waters network element
        :return: object of class DynamicObstacle according to the CommonOcean specification.
        """

        obstacle_type = DynamicObstacleFactory.read_type(xml_node)
        obstacle_id = DynamicObstacleFactory.read_id(xml_node)
        shape = DynamicObstacleFactory.read_shape(xml_node.find('shape'))
        initial_state = DynamicObstacleFactory.read_initial_state(xml_node.find('initialState'))
        depth = DynamicObstacleFactory.read_depth(xml_node)

        if xml_node.find('trajectory') is not None:

            trajectory = TrajectoryFactory.create_from_xml_node(xml_node.find('trajectory'))

            shape_waters_assignment = None
            center_waters_assignment = None

            prediction = TrajectoryPrediction(trajectory, shape, center_waters_assignment, shape_waters_assignment)

        elif xml_node.find('occupancySet') is not None:
            prediction = SetBasedPredictionFactory.create_from_xml_node(xml_node.find('occupancySet'))
        else:
            prediction = None
        return DynamicObstacle(obstacle_id=obstacle_id, obstacle_type=obstacle_type,
                               obstacle_shape=shape, initial_state=initial_state, prediction=prediction, depth=depth)


class TrajectoryFactory:
    """ Class to create a Trajectory from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) \
            -> Trajectory:
        """
        :param xml_node: XML element
        :return: object of class Trajectory according to the CommonOcean specification.
        """

        state_list = list()
        for state_node in xml_node.findall('state'):
            state_list.append(StateFactory.create_from_xml_node(state_node))
        if isinstance(state_list[0].time_step, Interval):
            t0 = min(state_list[0].time_step)
        else:
            t0 = state_list[0].time_step
        return Trajectory(t0, state_list)


class SetBasedPredictionFactory:
    """ Class to create a SetBasedPrediction from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> SetBasedPrediction:
        """
        :param xml_node: XML element
        :return: object of class SetBasedPrediction according to the CommonOcean specification.
        """

        occupancies = list()
        for occupancy in xml_node.findall('occupancy'):
            occupancies.append(OccupancyFactory.create_from_xml_node(occupancy))
        if isinstance(occupancies[0].time_step, Interval):
            t0 = min(occupancies[0].time_step)
        else:
            t0 = occupancies[0].time_step
        return SetBasedPrediction(t0, occupancies)


class OccupancyFactory:
    """ Class to create a Occupancy from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element) -> Occupancy:
        """
        :param xml_node: XML element
        :return: object of class Occupancy according to the CommonOcean specification.
        """

        shape = ShapeFactory.create_from_xml_node(xml_node.find('shape'))
        time = read_time(xml_node.find('time'))
        return Occupancy(time, shape)

class PlanningProblemSetFactory:
    """ Class to create a PlanningProblemSet from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element, waters_network: WatersNetwork) \
            -> PlanningProblemSet:
        """
        :param xml_node: XML element 
        :param waters_network: object of class WatersNetwork
        :return: object of class PlanningProblemSet according to the CommonOcean specification.
        """

        planning_problem_set = PlanningProblemSet()
        for p in xml_node.findall('planningProblem'):
            planning_problem_set.add_planning_problem(
                PlanningProblemFactory.create_from_xml_node(p, waters_network))
        return planning_problem_set

class PlanningProblemFactory:
    """ Class to create a PlanningProblem from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element, waters_network: WatersNetwork) \
            -> PlanningProblem:
        """
        :param xml_node: XML element 
        :param waters_network: object of class WatersNetwork
        :return: object of class PlanningProblem according to the CommonOcean specification.
        """

        planning_problem_id = int(xml_node.get('id'))
        initial_state = cls._add_initial_state(xml_node)
        goal_region = GoalRegionFactory.create_from_xml_node(xml_node, waters_network)
        if xml_node.find('waypoint') is not None:
            waypoints = WaypointFactory.create_from_xml_node(xml_node, waters_network)
        else:
            waypoints= None
        if xml_node.find('maxLateralDeviation') is not None:
            max_lateral_deviation = float(xml_node.get('maxLateralDeviation'))
        else:
            max_lateral_deviation = None
        return PlanningProblem(planning_problem_id, initial_state, goal_region, waypoints, max_lateral_deviation)

    @classmethod
    def _add_initial_state(cls, xml_node: ElementTree.Element) \
            -> State:
        """
        :param xml_node: XML element 
        :return: object of class CustomState according to the CommonRoad specification.
        """

        initial_state = StateFactory.create_from_xml_node(xml_node.find('initialState'))
        return initial_state


class GoalRegionFactory:
    """ Class to create a GoalRegion from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element, waters_network: WatersNetwork) \
            -> GoalRegion:
        """
        :param xml_node: XML element 
        :param waters_network: object of class WatersNetwork
        :return: object of class GoalRegion according to the CommonOcean specification.
        """

        state_list = list()
        waters_of_goal_position = defaultdict(list)
        for idx, goal_state_node in enumerate(xml_node.findall('goalState')):
            state_list.append(StateFactory.create_from_xml_node(goal_state_node, waters_network))
            if goal_state_node.find('position') is not None \
                    and goal_state_node.find('position').find('water') is not None:
                for f in goal_state_node.find('position').findall('water'):
                    waters_of_goal_position[idx].append(int(f.get('ref')))
        if not waters_of_goal_position:
            waters_of_goal_position = None
        return GoalRegion(state_list, waters_of_goal_position)

class WaypointFactory:
    """ Class to create a Waypoint from an XML element."""

    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element, waters_network: Union[WatersNetwork, None] = None) -> GoalRegion:
        """
        :param xml_node: XML element 
        :param waters_network: object of class WatersNetwork
        :return: object of class GoalRegion according to the CommonOcean specification.
        """

        waypoint_list = list()

        for waypoint_node in xml_node.findall('waypoint'):
            waypoint_list.append(GoalRegion([StateFactory.create_from_xml_node(waypoint_node, waters_network)]))
        return waypoint_list


class StateFactory:
    """ Class to create a CustomState from an XML element."""


    @classmethod
    def create_from_xml_node(cls, xml_node: ElementTree.Element, waters_network: Union[WatersNetwork, None] = None) \
            -> State:
        """
        :param xml_node: XML element 
        :param waters_network: object of class WatersNetwork
        :return: object of class CustomState according to the CommonOcean specification.
        """

        # Specific state classes
        states = [state_class() for state_class in SpecificStateClasses]
        used_fields = [element.tag for element in list(xml_node)]

        # Try to match the state with one of the specific state classes
        matched_state = None
        for state in states:
            if len(state.attributes) != len(used_fields):
                continue

            filled = StateFactory._fill_state(state, xml_node, state.attributes, waters_network)

            if filled:
                matched_state = state
                break

        else:
            # If no specific state class was found, use the custom state class
            matched_state = CustomState()
            StateFactory._fill_state(matched_state, xml_node, used_fields, waters_network)

        return matched_state

    @classmethod
    def _fill_state(cls, state: State, xml_node: ElementTree.Element, attrs: List[str],
                    waters_network: Union[WatersNetwork, None] = None) -> bool:
        """
        :param state: object of class CustomState according to the CommonOcean specification.
        :param xml_node: XML element
        :param attrs: list of attributes of the state
        :param waters_network: object of class WatersNetwork
        :return: True if all attributes of the state are filled, False otherwise.
        """
        attrs = [StateFactory._map_to_prop(attr) for attr in attrs]
        for attr in attrs:
            if attr == 'position' and xml_node.find('position') is not None:
                position = cls._read_position(xml_node.find('position'), waters_network)
                setattr(state, attr, position)
            elif attr == 'time_step' and xml_node.find('time') is not None:
                setattr(state, attr, read_time(xml_node.find('time')))
            elif attr == 'orientation' and xml_node.find(StateFactory._map_to_xml_prop(attr)) is not None:
                angle = cls._read_read_value_exact_or_angle_interval(xml_node.find(StateFactory._map_to_xml_prop(attr)))
                setattr(state, attr, angle)
            elif xml_node.find(StateFactory._map_to_xml_prop(attr)) is not None:
                value = read_value_exact_or_interval(xml_node.find(StateFactory._map_to_xml_prop(attr)))
                setattr(state, attr, value)
            else:
                return False
            
        return True
    

    @classmethod
    def _read_position(cls, xml_node: ElementTree.Element,
                       waters_network: Union[WatersNetwork, None] = None) \
            -> Union[np.ndarray, Shape]:
        """
        :param xml_node: XML element 
        :param waters_network: object of class WatersNetwork
        :return: position (np array) of the Shape according to the CommonOcean specification.
        """

        if xml_node.find('point') is not None:
            position = PointFactory.create_from_xml_node(xml_node.find('point'))
        elif (xml_node.find('rectangle') is not None
              or xml_node.find('circle') is not None
              or xml_node.find('polygon') is not None):
            position = ShapeFactory.create_from_xml_node(xml_node)
        elif waters_network is not None and xml_node.find('water') is not None:
            position_list = list()
            for l in xml_node.findall('water'):
                waterway = waters_network.find_waterway_by_id(int(l.get('ref')))
                polygon = waterway.convert_to_polygon()
                position_list.append(polygon)
            position = ShapeGroup(position_list)
        else:
            raise Exception()
        return position

    @classmethod
    def _read_read_value_exact_or_angle_interval(cls, xml_node: ElementTree.Element) -> Union[float, AngleInterval]:
        """
        :param xml_node: XML element 
        :return: float of AngleInterval according to the CommonOcean specification.
        """

        if xml_node.find('exact') is not None:
            value = float(xml_node.find('exact').text)
        elif xml_node.find('intervalStart') is not None \
                and xml_node.find('intervalEnd') is not None:
            value = AngleInterval(
                float(xml_node.find('intervalStart').text),
                float(xml_node.find('intervalEnd').text))
        else:
            raise Exception()
        return value
    
    @classmethod
    def _map_to_prop(cls, xml_prop: str) -> str:
        """
        :param xml_prop: property name in xml format
        :return: property name
        """
        if xml_prop == 'time':
            prop = 'time_step'
        else:
            prop = re.sub('(?<!^)(?=[A-Z])', '_', xml_prop).lower()
        return prop

    @classmethod
    def _map_to_xml_prop(cls, prop: str) -> str:
        """
        :param prop: property name
        :return: property name in xml format
        """
        if prop == 'time_step':
            xml_prop = 'time'
        else:
            xml_prop = re.sub(r'_(\w)', lambda m: m.group(1).upper(), prop)
        return xml_prop
    




