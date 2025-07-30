import datetime
import enum
import pathlib
import os
import re
from typing import Union, List, Set
import numpy as np
import decimal
import warnings

from commonocean import SCENARIO_VERSION
from lxml import etree, objectify

from commonroad.common.util import Interval
from commonroad.geometry.shape import Rectangle, Circle, ShapeGroup, Polygon
from commonocean.prediction.prediction import SetBasedPrediction, TrajectoryPrediction
from commonocean.scenario.trajectory import Trajectory
from commonroad.scenario.state import State, CustomState

from commonocean.planning.planning_problem import PlanningProblemSet, PlanningProblem
from commonocean.scenario.waters import Waters, WatersType, WatersNetwork, Waterway, Shallow
from commonocean.scenario.obstacle import ObstacleRole, ObstacleType, DynamicObstacle, StaticObstacle, Obstacle, \
    Occupancy, Shape
from commonocean.scenario.scenario import Scenario, Tag, Location, GeoTransformation, Weather, Environment, SeaState, TimeOfDay
from commonocean.scenario.traffic_sign import TrafficSign

# Tunneling from CR-IO #
from commonroad.common.writer.file_writer_xml import float_to_str as float_to_str_CR
from commonroad.common.writer.file_writer_xml import create_exact_node_float as create_exact_node_float_CR
from commonroad.common.writer.file_writer_xml import create_exact_node_int as create_exact_node_int_CR
from commonroad.common.writer.file_writer_xml import create_interval_node_float as create_interval_node_float_CR
from commonroad.common.writer.file_writer_xml import create_interval_node_int as create_interval_node_int_CR
from commonroad.common.writer.file_writer_xml import Point, Pointlist
########################

__author__ = "Hanna Krasowski, Benedikt Pfleiderer, Fabian Thomas-Barein"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"

"""
File Writer for scenarios to commonocean xml-format
"""

class DecimalPrecision:
    """
    Represents the decimal precision of the process
    """

    decimals = 4

precision = DecimalPrecision

def float_to_str(f):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    return float_to_str_CR(f)


def create_exact_node_float(value: Union[int, float]) -> etree.Element:
    """
    creates element node for exact value
    :param value: exact value
    :return: node for exact value
    """
    return create_exact_node_float_CR(value)


def create_exact_node_int(value: Union[int]) -> etree.Element:
    """
    creates element node for exact value
    :param value: exact value
    :return: node for exact value
    """
    return create_exact_node_int_CR(value)


def create_interval_node_float(interval: Interval) -> List[etree.Element]:
    """
    creates ElementTree.Element for an interval
    :param interval:
    :return: list of Element nodes with start and end of interval
    """
    return create_interval_node_float_CR(interval)


def create_interval_node_int(interval: Interval) -> List[etree.Element]:
    """
    creates ElementTree.Element for an interval
    :param interval:
    :return: list of Element nodes with start and end of interval
    """
    return create_interval_node_int_CR(interval)


class OverwriteExistingFile(enum.Enum):
    """
    Specifies whether an existing file will be overwritten or skipped
    """

    ASK_USER_INPUT = 0
    ALWAYS = 1
    SKIP = 2


class CommonOceanFileWriter:
    def __init__(
        self,
        scenario: Scenario,
        planning_problem_set: PlanningProblemSet,
        author: str = None,
        affiliation: str = None,
        source: str = None,
        tags: Set[Tag] = None,
        location: Location = None,
        decimal_precision: int = 8,
    ):
        """
        Initialize the FileWriter with a scenario and tags for the xml-header

        :param scenario: scenario that should be written later
        :param planning_problem_set: corresponding planning problem to the scenario
        :param author: author's name
        :param affiliation: affiliation of the author
        :param source: source of dataset (d.h. database, handcrafted, etc.)
        :param tags: list of keywords describing the scenario (e.g. waters type,
                required maneuver etc., see commonocean.cps.cit.tum.de for full list))
        :param decimal_precision: number of decimal places used when writing float values
        """
        assert not (author is None and scenario.author is None)
        assert not (affiliation is None and scenario.affiliation is None)
        assert not (source is None and scenario.source is None)
        assert not (tags is None and scenario.tags is None)

        self.scenario: Scenario = scenario
        self.planning_problem_set: PlanningProblemSet = planning_problem_set
        self._root_node = etree.Element('commonOcean')
        self.author = author if author is not None else scenario.author
        self.affiliation = affiliation if affiliation is not None else scenario.affiliation
        self.source = source if source is not None else scenario.source
        self.location = location if location is not None else scenario.location
        self.tags = tags if tags is not None else scenario.tags

        precision.decimals = decimal_precision

    @property
    def root_node(self):
        """ Root node of the scenario """
        return self._root_node

    @root_node.setter
    def root_node(self, root_node):
        warnings.warn(
            '<CommonOceanFileWriter/root_node> root_node of CommonOceanFileWriter is immutable'
        )

    @property
    def author(self):
        """ Author of the scenario """
        return self._author

    @author.setter
    def author(self, author):
        assert isinstance(
            author, str
        ), '<CommonOceanFileWriter/author> author must be a string, but has type {}'.format(
            type(author)
        )
        self._author = author

    @property
    def affiliation(self):
        """ Affiliation of the author """
        return self._affiliation

    @affiliation.setter
    def affiliation(self, affiliation):
        assert isinstance(
            affiliation, str
        ), '<CommonOceanFileWriter/affiliation> affiliation must be a string, but has type {}'.format(
            type(affiliation)
        )
        self._affiliation = affiliation

    @property
    def source(self):
        """ Source of the scenario """
        return self._source

    @source.setter
    def source(self, source):
        assert isinstance(
            source, str
        ), '<CommonOceanFileWriter/source> source must be a string, but has type {}'.format(
            type(source)
        )
        self._source = source

    @property
    def tags(self):
        """ Tags of the scenario """
        return self._tags

    @tags.setter
    def tags(self, tags):
        for tag in tags:
            assert isinstance(tag, Tag), '<CommonOceanFileWriter/tags> tag must ' \
                                         'be a enum of type Tag, but has type {}'.format(type(tag))
        self._tags = tags

    def _write_header(self):
        self._root_node.set('timeStepSize', str(self.scenario.dt))
        self._root_node.set('commonOceanVersion', SCENARIO_VERSION)
        self._root_node.set('author', self.author)
        self._root_node.set('affiliation', self.affiliation)
        self._root_node.set('source', self.source)

        try:
            if self.scenario.scenario_id:
                self._root_node.set('benchmarkID', str(self.scenario.scenario_id))
        except:
            self._root_node.set('benchmarkID', '-1')
            print('Warning: No scenario_id set.')

        self._root_node.set('date', datetime.datetime.today().strftime('%Y-%m-%d'))

    def _add_all_objects_from_scenario(self):
        if self.location is not None:
            self._root_node.append(LocationXMLNode.create_node(self.location))
        else:
            self._root_node.append(LocationXMLNode.create_node(Location()))
        self._root_node.append(TagXMLNode.create_node(self.tags))
        self._root_node.append(WatersNetworkXMLNode.create_node(self.scenario._waters_network))
        for w in self.scenario.waterways:
            self._root_node.append(WaterwaysXMLNode.create_node(w))
        for s in self.scenario.shallows:
            self._root_node.append(ShallowXMLNode.create_node(s))
        for sign in self.scenario._waters_network.traffic_signs:
            self._root_node.append(TrafficSignXMLNode.create_node(sign))
        for o in self.scenario.obstacles:
            self._root_node.append(ObstacleXMLNode.create_node(o))

    def _add_all_planning_problems_from_planning_problem_set(self):
        for (
            planning_problem
        ) in self.planning_problem_set.planning_problem_dict.values():
            self._root_node.append(PlanningProblemXMLNode.create_node(planning_problem))

    def _dump(self):
        rough_string = etree.tostring(
            self._root_node, pretty_print=True, encoding='UTF-8'
        )
        rough_string = rough_string
        return rough_string

    def write_to_file(
        self,
        filename: Union[str, None] = None,
        overwrite_existing_file: OverwriteExistingFile = OverwriteExistingFile.ASK_USER_INPUT,
        check_validity: bool = False
    ):
        """
        Write a scenario including planning-problem. If file already exists, it will be overwritten of skipped

        :param filename: filename of the xml output file. If 'None', the Benchmark ID is taken
        :param overwrite_existing_file: Specify whether an already existing file should be overwritten or skipped
        :param check_validity: check xml file against .xsd definition
        """
        if filename is None:
            filename = str(self.scenario.scenario_id)

        if pathlib.Path(filename).is_file():
            if overwrite_existing_file is OverwriteExistingFile.ASK_USER_INPUT:
                overwrite = input(
                    'File {} already exists, replace old file (or else skip)? (y/n)'.format(
                        filename
                    )
                )
            elif overwrite_existing_file is OverwriteExistingFile.SKIP:
                overwrite = 'n'
            else:
                overwrite = 'y'

            if overwrite == 'n':
                print('Writing of file {} skipped'.format(filename))
                return
            else:
                print('Replace file {}'.format(filename))

        self._write_header()
        self._add_all_objects_from_scenario()
        self._add_all_planning_problems_from_planning_problem_set()
        if check_validity:
            self.check_validity_of_commonocean_file(self._dump())

        tree = etree.ElementTree(self._root_node)
        tree.write(filename, pretty_print=True, xml_declaration=True, encoding="utf-8")

    def write_scenario_to_file(
        self,
        filename: Union[str, None] = None,
        overwrite_existing_file: OverwriteExistingFile = OverwriteExistingFile.ASK_USER_INPUT
    ):
        """
        Write a scenario without planning-problem. If file already exists, it will be overwritten of skipped.

        :param filename: filename of the xml output file. If 'None', the Benchmark ID is taken
        :param OverwriteExistingFile: Specify whether an already existing file should be overwritten or skipped
        """
        if filename is None:
            filename = str(self.scenario.scenario_id)

        if pathlib.Path(filename).is_file():
            if overwrite_existing_file is OverwriteExistingFile.ASK_USER_INPUT:
                overwrite = input(
                    'File {} already exists, replace old file (or else skip)? (y/n)'.format(
                        filename
                    )
                )
            elif overwrite_existing_file is OverwriteExistingFile.SKIP:
                overwrite = 'n'
            else:
                overwrite = 'y'

            if overwrite == 'n':
                print(
                    'Writing skipped for file, since it already exists {}'.format(
                        filename
                    )
                )
                return
            else:
                print('Replace file {}'.format(filename))

        self._write_header()
        self._add_all_objects_from_scenario()

        tree = etree.ElementTree(self._root_node)
        tree.write(filename, pretty_print=True, xml_declaration=True, encoding="utf-8")

    @staticmethod
    def check_validity_of_commonocean_file(commonocean_str: str):
        """Check the validity of a generated xml_string in terms of
        commonocean with an existing XSD schema.
        Throw an error if it is not valid.

        :param commonocean_str: string of the commonocean file
        :raises Exception: if the file is not valid
        """
        with open(
            os.path.dirname(os.path.abspath(__file__)) + '/XML_commonOcean_XSD.xsd',
            'rb',
        ) as schema_file:
            schema = etree.XMLSchema(etree.parse(schema_file))

        parser = objectify.makeparser(schema=schema, encoding='utf-8')

        try:
            etree.fromstring(commonocean_str, parser)
        except etree.XMLSyntaxError as error:
            raise Exception(
                'Could not produce valid CommmonOcean file! Error: {}'.format(error.msg)
            )


class LocationXMLNode:
    """ Class to create a XML element from a Location."""

    @classmethod
    def create_node(cls, location: Location) -> etree.Element:
        """
        Create XML-Node for a location
        :param location: location object
        :return: node
        """
        location_node = etree.Element('location')
        geo_name_id_node = etree.Element("geoNameId")
        geo_name_id_node.text = str(location.geo_name_id)
        location_node.append(geo_name_id_node)
        gps_latitude_node = etree.Element("gpsLatitude")
        gps_latitude_node.text = str(location.gps_latitude)
        location_node.append(gps_latitude_node)
        gps_longitude_node = etree.Element("gpsLongitude")
        gps_longitude_node.text = str(location.gps_longitude)
        location_node.append(gps_longitude_node)
        if location.geo_transformation is not None:
            location_node.append(GeoTransformationXMLNode.create_node(location.geo_transformation))
        if location.environment is not None:
            location_node.append(EnvironmentXMLNode.create_node(location.environment))
        return location_node


class GeoTransformationXMLNode:
    """ Class to create a XML element from a GeoTransformation."""

    @classmethod
    def create_node(cls, geo_transformation: GeoTransformation) -> etree.Element:
        """
        Create XML-Node for a location
        :param geo_transformation: GeoTransformation object
        :return: node
        """
        geotransform_node = etree.Element('geoTransformation')
        geo_reference_node = etree.Element("geoReference")
        geo_reference_node.text = geo_transformation.geo_reference
        geotransform_node.append(geo_reference_node)
        additional_transformation_node = etree.Element('additionalTransformation')
        x_translation_node = etree.Element("xTranslation")
        x_translation_node.text = str(geo_transformation.x_translation)
        additional_transformation_node.append(x_translation_node)
        y_translation_node = etree.Element("yTranslation")
        y_translation_node.text = str(geo_transformation.y_translation)
        additional_transformation_node.append(y_translation_node)
        z_rotation_node = etree.Element("zRotation")
        z_rotation_node.text = str(geo_transformation.z_rotation)
        additional_transformation_node.append(z_rotation_node)
        scaling_node = etree.Element("scaling")
        scaling_node.text = str(geo_transformation.scaling)
        additional_transformation_node.append(scaling_node)
        geotransform_node.append(additional_transformation_node)

        return geotransform_node


class EnvironmentXMLNode:
    """ Class to create a XML element from a Environment."""

    @classmethod
    def create_node(cls, environment: Environment) -> etree.Element:
        """
        Create XML-Node for a environment
        :param environment: Environment object
        :return: node
        """
        environment_node = etree.Element('environment')
        if environment.time_of_day.value is not TimeOfDay.UNKNOWN:
            time_node = etree.Element('time')
            if environment.time.month < 10:
                time_node.text = str(environment.time.year) + "-0" + str(environment.time.month)
            else:
                time_node.text = str(environment.time.year) + "-" + str(environment.time.month)
            if environment.time.day < 10:
                time_node.text = time_node.text + "-0" + str(environment.time.day)
            else:
                time_node.text = time_node.text + "-" + str(environment.time.day)
            if environment.time.hours < 10:
                time_node.text = time_node.text + "-0" + str(environment.time.hours)
            else:
                time_node.text = time_node.text + "-0" + str(environment.time.hours)
            if environment.time.minutes < 10:
                time_node.text = time_node.text + ":0" + str(environment.time.minutes)
            else:
                time_node.text = time_node.text + ":" + str(environment.time.minutes)
            environment_node.append(time_node)
            time_of_day_node = etree.Element('timeOfDay')
            time_of_day_node.text = environment.time_of_day.value
            environment_node.append(time_of_day_node)
        if environment.weather.value is not None:
            weather_node = etree.Element('weather')
            weather_node.text = environment.weather.value
            environment_node.append(weather_node)
        if environment.seastate.value is not None:
            underground_node = etree.Element('seaState')
            underground_node.text = environment.seastate.value
            environment_node.append(underground_node)

        return environment_node

class TagXMLNode:
    """ Class to create a XML element from a Tag."""

    @classmethod
    def create_node(cls, tags: Set[Tag]) -> etree.Element:
        """
        Create XML-Node for a tag element
        :param tags: list of tags of the scenario
        :return: node
        """
        tags_node = etree.Element('scenarioTags')
        for tag in tags:
            tags_node.append(etree.Element(tag.value))

        return tags_node

class WatersNetworkXMLNode:
    """ Class to create a XML element from a WatersNetwork."""

    @classmethod
    def create_node(cls, watersnetwork: WatersNetwork) -> etree.Element:
        """
        Create XML-Node for a waters network element
        :param watersnetwork: list of  of the scenario
        :return: node
        """
        watersnetwork_node = etree.Element('navigationableArea')
        watersnetwork_node.extend(ShapeXMLNode.create_node(watersnetwork.navigationable_area))

        return watersnetwork_node


class WaterwaysXMLNode:
    """ Class to create a XML element from a Waterway."""

    @classmethod
    def create_node(cls, waters: Waterway) -> etree.Element:
        """
        Create XML-Node for a Water
        :param waters: water for creating a node
        :return: node
        """
        waters_node = etree.Element('waterway')
        waters_node.set('id', str(waters.waters_id))

        left_boundary = etree.Element('leftBound')
        Pointlist.create_from_numpy_array(waters.left_vertices).add_points_to_node(
            left_boundary
        )

        waters_node.append(left_boundary)

        right_boundary = etree.Element('rightBound')
        Pointlist.create_from_numpy_array(waters.right_vertices).add_points_to_node(
            right_boundary
        )

        waters_node.append(right_boundary)

        depth_node = etree.Element('depth')
        depth_node.append(create_exact_node_float(waters.depth))
        waters_node.append(depth_node)

        waters_type_node = etree.Element('watersType')
        waters_type_node.text = str(waters.waters_type.value)
        waters_node.append(waters_type_node)

        for l in waters.predecessor:
            predecessor = etree.Element('predecessor')
            predecessor.set('ref', str(l))
            waters_node.append(predecessor)

        for l in waters.successor:
            successor = etree.Element('successor')
            successor.set('ref', str(l))
            waters_node.append(successor)

        if waters.traffic_signs:
            for traffic_sign in waters.traffic_signs:
                traffic_sign_node = TrafficSignXMLNode.create_ref_node(traffic_sign)
                waters_node.append(traffic_sign_node)

        return waters_node


class ShallowXMLNode:
    """ Class to create a XML element from a Shallow."""

    @classmethod
    def create_node(cls, shallow: Shallow) -> etree.Element:
        """
        Create XML-Node for a Shallow
        :param shallow: shallow for creating a node
        :return: node
        """
        shallow_node = etree.Element('shallow')
        shallow_node.set('id', str(shallow.waters_id))

        shape_node = etree.Element('shape')
        shape_node.extend(ShapeXMLNode.create_node(shallow.shape))
        shallow_node.append(shape_node)

        depth_node = etree.Element('depth')
        depth_node.append(create_exact_node_float(shallow.depth))
        shallow_node.append(depth_node)

        waters_type_node = etree.Element('watersType')
        waters_type_node.text = str(shallow.waters_type.value)
        shallow_node.append(waters_type_node)

        return shallow_node


class ObstacleXMLNode:
    """ Class to create a XML element from an Obstacle."""

    @classmethod
    def create_node(cls, obstacle: Union[Obstacle, DynamicObstacle, StaticObstacle]) -> etree.Element:
        """
        Create XML-Node for an Obstacle
        :param obstacle: Obstacle for creating a node
        :return:
        """
        if type(obstacle) == DynamicObstacle:
            return DynamicObstacleXMLNode.create_node(obstacle)
        elif type(obstacle) == StaticObstacle:
            return StaticObstacleXMLNode.create_node(obstacle)
        else:
            raise Exception()

    @classmethod
    def create_obstacle_node_header(
        cls, obstacle_id: int, obstacle_role: ObstacleRole, obstacle_type: ObstacleType, depth: float
    ):
        """
        Create the header of XML-Node for an Obstacle
        :param obstacle_id: id of the obstacle
        :param obstacle_role: role of the obstacle
        :param obstacle_type: type of the obstacle
        :return: node
        """
        obstacle_node = etree.Element(obstacle_role.value+'Obstacle')
        obstacle_node.set('id', str(obstacle_id))
        type_node = etree.Element('type')
        type_node.text = obstacle_type.value
        obstacle_node.append(type_node)
        depth_node = etree.Element('depth')
        depth_node.text = str(depth)
        obstacle_node.append(depth_node)
        return obstacle_node


class StaticObstacleXMLNode:
    """ Class to create a XML element from a StaticObstacle."""

    @classmethod
    def create_node(cls, static_obstacle: StaticObstacle) -> etree.Element:
        """
        Create XML-Node for a StaticObstacle
        :param static_obstacle: static_obstacle for creating a node
        :return: node
        """
        node = ObstacleXMLNode.create_obstacle_node_header(
            static_obstacle.obstacle_id,
            static_obstacle.obstacle_role,
            static_obstacle.obstacle_type,
            static_obstacle.depth
        )
        shape_node = etree.Element('shape')
        shape_node.extend(ShapeXMLNode.create_node(static_obstacle.obstacle_shape))
        node.append(shape_node)

        initial_state_node = etree.Element('initialState')
        StateXMLNode.create_state_node(
            static_obstacle.initial_state,
            initial_state_node,
            time_step=static_obstacle.initial_state.time_step,
        )
        node.append(initial_state_node)

        return node


class DynamicObstacleXMLNode:
    """ Class to create a XML element from a DynamicObstacle."""

    @classmethod
    def create_node(cls, dynamic_obstacle: DynamicObstacle) -> etree.Element:
        """
        Create XML-Node for a DynamicObstacle
        :param dynamic_obstacle: dynamic_obstacle for creating a node
        :return: node
        """
        obstacle_node = ObstacleXMLNode.create_obstacle_node_header(
            dynamic_obstacle.obstacle_id,
            dynamic_obstacle.obstacle_role,
            dynamic_obstacle.obstacle_type,
            dynamic_obstacle.depth
        )
        shape_node = etree.Element('shape')
        shape_node.extend(
            ShapeXMLNode.create_node(
                dynamic_obstacle.obstacle_shape, dynamic_obstacle_shape=True
            )
        )
        obstacle_node.append(shape_node)

        initial_state_node = etree.Element('initialState')
        StateXMLNode.create_state_node(
            dynamic_obstacle.initial_state,
            initial_state_node,
            time_step=dynamic_obstacle.initial_state.time_step,
        )
        obstacle_node.append(initial_state_node)

        if isinstance(dynamic_obstacle.prediction, SetBasedPrediction):
            obstacle_node.append(
                cls._create_occupancy_node(dynamic_obstacle.prediction.occupancy_set)
            )
        elif isinstance(dynamic_obstacle.prediction, TrajectoryPrediction):
            obstacle_node.append(
                cls._create_trajectory_node(dynamic_obstacle.prediction.trajectory)
            )

        return obstacle_node

    @classmethod
    def _create_trajectory_node(cls, trajectory: Trajectory) -> etree.Element:
        """
        Create XML-Node for a Trajectory
        :param trajectory: trajectory for creating a node
        :return: node
        """
        traj_node = etree.Element('trajectory')
        for state in trajectory.state_list:
            state_node = etree.Element('state')
            traj_node.append(
                StateXMLNode.create_state_node(state, state_node, state.time_step)
            )
        return traj_node

    @classmethod
    def _create_occupancy_node(cls, occupancy_set: List[Occupancy]) -> etree.Element:
        """
        Create XML-Node for an occupancy_set
        :param occupancy_set: occupancy_set for creating a node
        :return: node
        """
        occupancy_set_node = etree.Element('occupancySet')
        for occupancy in occupancy_set:
            occupancy_set_node.append(OccupancyXMLNode.create_node(occupancy))
        return occupancy_set_node


class OccupancyXMLNode:
    """ Class to create a XML element from a Occupancy."""

    @classmethod
    def create_node(cls, occupancy: Occupancy) -> etree.Element:
        """
        Create XML-Node for an Occupancy
        :param occupancy: occupancy for creating a node
        :return: node
        """
        occupancy_node = etree.Element('occupancy')

        shape_node = etree.Element('shape')
        shape_node.extend(ShapeXMLNode.create_node(occupancy.shape))
        occupancy_node.append(shape_node)

        time_node = etree.Element('time')
        time = occupancy.time_step
        if isinstance(occupancy.time_step, Interval):
            time_node.extend(create_interval_node_int(time))
        else:
            time_node.append(create_exact_node_int(time))
        occupancy_node.append(time_node)

        return occupancy_node



class ShapeXMLNode:
    """ Class to create a XML element from a Shape."""

    @classmethod
    def create_node(cls, shape, dynamic_obstacle_shape=False) -> List[etree.Element]:
        """
        Create XML-Node for a shape
        :param shape: shape for creating a node
        :param dynamic_obstacle_shape: specify whether the shape belongs to an dynamic obstacle or not
        :return: node
        """
        if type(shape) == ShapeGroup:
            shape_node_list = []
            for s in shape.shapes:
                shape_node_list.append(
                    cls._create_single_element(s, dynamic_obstacle_shape)
                )
        else:
            shape_node = cls._create_single_element(shape, dynamic_obstacle_shape)
            shape_node_list = [shape_node]
        return shape_node_list

    @classmethod
    def _create_single_element(
        cls, shape: Shape, dynamic_obstacle_shape: bool
    ) -> etree.Element:
        """
        Create XML-Node for a single shape element
        :param shape: shape for creating a node
        :param dynamic_obstacle_shape: specify whether the shape belongs to an dynamic obstacle or not
        :return: node
        """
        if type(shape) == Rectangle:
            node = RectangleXMLNode.create_rectangle_node(shape, dynamic_obstacle_shape)
        elif type(shape) == Circle:
            node = CircleXMLNode.create_circle_node(shape, dynamic_obstacle_shape)
        elif type(shape) == Polygon:
            node = PolygonXMLNode.create_polygon_node(shape, dynamic_obstacle_shape)
        else:
            raise TypeError(
                '<ShapeXMLNode/_create_single_element> Expected type Polygon, Circle or Rectangle but got %s'
                % (type(shape))
            )
        return node


class RectangleXMLNode:
    """ Class to create a XML element from a Rectangle."""

    @classmethod
    def create_rectangle_node(
        cls, rectangle: Rectangle, dynamic_obstacle_shape=False
    ) -> etree.Element:
        """
        Create XML-Node for a rectangle
        :param rectangle: rectangle for creating a node
        :param dynamic_obstacle_shape: specify whether the shape belongs to an dynamic obstacle or not
        :return: node
        """
        rectangle_node = etree.Element('rectangle')
        length_node = etree.Element('length')
        length_node.text = str(rectangle.length)
        rectangle_node.append(length_node)

        width_node = etree.Element('width')
        width_node.text = str(rectangle.width)
        rectangle_node.append(width_node)

        if not dynamic_obstacle_shape:
            orientation_node = etree.Element('orientation')
            orientation_node.text = str(np.float64(rectangle.orientation))
            rectangle_node.append(orientation_node)

            center_node = etree.Element('center')
            x_node = etree.Element('x')
            x_node.text = str(np.float64(rectangle.center[0]))
            center_node.append(x_node)
            y_node = etree.Element('y')
            y_node.text = str(np.float64(rectangle.center[1]))
            center_node.append(y_node)
            rectangle_node.append(center_node)
        return rectangle_node


class CircleXMLNode:
    """ Class to create a XML element from a Circle."""

    @classmethod
    def create_circle_node(
        cls, circle: Circle, dynamic_obstacle_shape=False
    ) -> etree.Element:
        """
        Create XML-Node for a circle
        :param circle: circle for creating a node
        :param dynamic_obstacle_shape: specify whether the shape belongs to an dynamic obstacle or not
        :return: node
        """
        circle_node = etree.Element('circle')

        radius_node = etree.Element('radius')
        radius_node.text = str(np.float64(circle.radius))
        circle_node.append(radius_node)

        if not dynamic_obstacle_shape:
            center_node = etree.Element('center')
            x_node = etree.Element('x')
            x_node.text = str(np.float64(circle.center[0]))
            center_node.append(x_node)
            y_node = etree.Element('y')
            y_node.text = str(np.float64(circle.center[1]))
            center_node.append(y_node)
            circle_node.append(center_node)
        return circle_node


class PolygonXMLNode:
    """ Class to create a XML element from a Polygon."""

    @classmethod
    def create_polygon_node(
        cls, polygon: Polygon, dynamic_obstacle_shape: bool = False
    ) -> etree.Element:
        """
        Create XML-Node for a polygon
        :param polygon: polygon for creating a node
        :param dynamic_obstacle_shape: specify whether the shape belongs to an dynamic obstacle or not
        :return: node
        """
        polygon_node = etree.Element('polygon')
        for p in polygon.vertices:
            polygon_node.append(Point(p[0], p[1]).create_node())
        return polygon_node


class StateXMLNode:
    """ Class to create a XML element from a CustomState."""

    @classmethod
    def create_waypoint_node(cls, state: State, waypoint_water_ids: List[int]) -> etree.Element:
        """
        Create XML-Node for a state
        :param state: CommonOcean state
        :param waypoint_water_ids: contains a list of water ids if a waypoint state's position is specified water id(s)
        :return: node
        """
        state_node = etree.Element('waypoint')
        if hasattr(state, 'position') or len(waypoint_water_ids) > 0:
            position = etree.Element('position')
            position = cls._write_goal_position(position, state.position, waypoint_water_ids)
            state_node.append(position)

        if hasattr(state, 'orientation'):
            orientation = etree.Element('orientation')
            orientation = cls._write_value_exact_or_interval(
                orientation, state.orientation
            )
            state_node.append(orientation)
        if hasattr(state, 'time_step'):
            time = etree.Element('time')
            time = cls._write_goal_time_exact_or_interval(time, state.time_step)
            state_node.append(time)
        if hasattr(state, 'velocity'):
            velocity = etree.Element('velocity')
            velocity = cls._write_value_exact_or_interval(velocity, state.velocity)
            state_node.append(velocity)
        if hasattr(state, 'acceleration'):
            acceleration = etree.Element('acceleration')
            acceleration = cls._write_value_exact_or_interval(
                acceleration, state.acceleration
            )
            state_node.append(acceleration)
        if hasattr(state, 'yaw_rate'):
            yaw_rate = etree.Element('yawRate')
            yaw_rate = cls._write_value_exact_or_interval(yaw_rate, state.yaw_rate)
            state_node.append(yaw_rate)
        return state_node

    @classmethod
    def create_goal_state_node(cls, state: State, goal_waters_ids: List[int]) -> etree.Element:
        """
        Create XML-Node for a state
        :param state: CommonOcean state
        :param goal_waters_ids: contains a list of water ids if a goal state's position is specified water id(s)
        :return: node
        """
        state_node = etree.Element('goalState')
        if hasattr(state, 'position') or len(goal_waters_ids) > 0:
            position = etree.Element('position')
            position = cls._write_goal_position(position, state.position, goal_waters_ids)
            state_node.append(position)

        if hasattr(state, 'orientation'):
            orientation = etree.Element('orientation')
            orientation = cls._write_value_exact_or_interval(
                orientation, state.orientation
            )
            state_node.append(orientation)
        if hasattr(state, 'time_step'):
            time = etree.Element('time')
            time = cls._write_goal_time_exact_or_interval(time, state.time_step)
            state_node.append(time)
        if hasattr(state, 'velocity'):
            velocity = etree.Element('velocity')
            velocity = cls._write_value_exact_or_interval(velocity, state.velocity)
            state_node.append(velocity)
        if hasattr(state, 'acceleration'):
            acceleration = etree.Element('acceleration')
            acceleration = cls._write_value_exact_or_interval(
                acceleration, state.acceleration
            )
            state_node.append(acceleration)
        if hasattr(state, 'yaw_rate'):
            yaw_rate = etree.Element('yawRate')
            yaw_rate = cls._write_value_exact_or_interval(yaw_rate, state.yaw_rate)
            state_node.append(yaw_rate)
        return state_node

    @classmethod
    def _write_goal_position(
        cls, node: etree.Element, position: Union[Shape, int, list], goal_waters_ids: List[int],
    ) -> etree.Element:
        """
        Create XML-Node for a goal position
        :param node: node of the GoalState
        :param position: either (list of) shape elements or water ids specifying the goal position
        :return: node
        """
        if len(goal_waters_ids) > 0:
            for id in goal_waters_ids:
                waters = etree.Element('water')
                waters.set('ref', str(id))
                node.append(waters)
        elif isinstance(position, int):
            waters = etree.Element('water')
            waters.set('ref', str(position))
            node.append(waters)
        elif(
            isinstance(position, Rectangle)
            or isinstance(position, Circle)
            or isinstance(position, Polygon)
            ):
            node.extend(ShapeXMLNode.create_node(position))
        elif isinstance(position, ShapeGroup):
            node.extend(ShapeXMLNode.create_node(position))
        elif type(position) is list:
            raise ValueError('A goal state cannot contain multiple items. Use a list of goal states instead.')
        else:
            raise ValueError('Case should not occur, position={}, goal_waters_ids={}.'.format(position,
                                                                                               goal_waters_ids))
        return node

    @classmethod
    def _write_goal_time_exact_or_interval(
        cls, node: etree.Element, time_step: Union[Interval, float, int]
    ) -> etree.Element:
        """
        Create XML-Node for a goal time
        :param node: node of the GoalState
        :param time_step: contains time interval or time_step of goal time
        :return: node
        """
        if isinstance(time_step, int):
            node.append(create_exact_node_int(time_step))
        elif isinstance(time_step, Interval):
            node.extend(
                create_interval_node_int(Interval(time_step.start, time_step.end))
            )
        else:
            raise Exception()
        return node

    @classmethod
    def _write_value_exact_or_interval(
        cls, node: etree.Element, var: Union[Interval, float, int]
    ):
        """
        Create XML-Node for a goal value
        :param node: node of the GoalState
        :param var: contains interval or exact_value of goal state value
        :return: node
        """
        if isinstance(var, (float, int)):
            node.append(create_exact_node_float(var))
        elif isinstance(var, Interval):
            node.extend(create_interval_node_float(var))
        else:
            raise Exception()
        return node

    @classmethod
    def create_state_node(
        cls, state: State, state_node: etree.Element, time_step: int
    ) -> etree.Element:
        """
        Create XML-Node for a state
        :param state: value of the state
        :param state_node: node of the overlying state
        :return: node
        """

        state_type = type(state)
        for attr in state.used_attributes:

            if attr == "time_step":
                time_node = etree.Element("time")
                time_node.append(create_exact_node_int(time_step))
                state_node.append(time_node)

            # Check if the attribute is defined in the state class
            elif state_type == CustomState or attr in state_type.__annotations__:

                if attr == 'position':
                    position = etree.Element('position')
                    if type(state.position) in [np.ndarray, list]:
                        position.append(
                            Point.create_from_numpy_array(state.position).create_node()
                        )
                        state_node.append(position)
                    elif isinstance(state.position, Shape):
                        position.extend(ShapeXMLNode.create_node(state.position))
                        state_node.append(position)

                elif getattr(state, attr) is not None:
                    # Regex to convert snake_case to camelCase
                    element = etree.Element(re.sub(r'_(\w)', lambda m: m.group(1).upper(), attr))
                    element = cls._write_value_exact_or_interval(element, getattr(state, attr))
                    state_node.append(element)

        return state_node


class PlanningProblemXMLNode:
    """ Class to create a XML element from a PlanningProblem."""

    @classmethod
    def create_node(cls, planning_problem: PlanningProblem) -> etree.Element:
        """
        Create a xml-Node for a single planning_problem
        :param planning_problem: planning problem for creating the node
        :return:
        """
        planning_problem_node = etree.Element('planningProblem')
        planning_problem_node.set('id', str(planning_problem.planning_problem_id))
        if planning_problem.max_lateral_deviation is not None:
            planning_problem_node.set('maxLateralDeviation', str(planning_problem.max_lateral_deviation))
        
        initial_state_node = etree.Element('initialState')
        planning_problem_node.append(
            StateXMLNode.create_state_node(
                planning_problem.initial_state,
                initial_state_node,
                planning_problem.initial_state.time_step,
            )
        )

        for state_id, goal_state in enumerate(planning_problem.goal.state_list):
            if (
                planning_problem.goal.waters_of_goal_position is not None
                and state_id in planning_problem.goal.waters_of_goal_position
            ):
                goal_waters_ids: List[
                    int
                ] = planning_problem.goal.waters_of_goal_position[state_id]
            else:
                goal_waters_ids = []

            planning_problem_node.append(
                StateXMLNode.create_goal_state_node(goal_state, goal_waters_ids)
            )
        if planning_problem.waypoints is not None:
            for waypoint in planning_problem.waypoints:
                state = waypoint.state_list[0]
                planning_problem_node.append(
                    StateXMLNode.create_waypoint_node(state, [])
                )


        return planning_problem_node

class TrafficSignXMLNode:
    """ Class to create a XML element from a TrafficSign."""

    @classmethod
    def create_node(cls, traffic_sign: TrafficSign) -> etree.Element:
        """
        Create XML-Node for a state
        :param traffic_sign: TrafficSign object
        :return: node
        """

        traffic_sign_node = etree.Element('trafficSign')
        traffic_sign_node.set('id', str(traffic_sign.traffic_sign_id))
        for element in traffic_sign.traffic_sign_elements:
            element_node = etree.Element('trafficSignElement')
            sign_id_node = etree.Element('trafficSignID')
            sign_id_node.text = str(element.traffic_sign_element_id.value)
            if str(element.traffic_sign_element_id.value) == '':
                warnings.warn('<FileWriter>: Invalid traffic sign ID!')
            element_node.append(sign_id_node)
            for value in element.additional_values:
                value_node = etree.Element('additionalValue')
                value_node.text = str(value)
                element_node.append(value_node)
            traffic_sign_node.append(element_node)

        if traffic_sign.position is not None:
            position_node = etree.Element('position')
            position_node.append(Point(traffic_sign.position[0],
                                       traffic_sign.position[1]).create_node())
            traffic_sign_node.append(position_node)

        if traffic_sign.virtual is not None:
            virtual_node = etree.Element('virtual')
            virtual_node.text = str(traffic_sign.virtual).lower()
            traffic_sign_node.append(virtual_node)

        if traffic_sign.related_obstacle is not None:
            related_obstacle_ref_node = etree.Element('relatedObstacleRef')
            related_obstacle_ref_node.set('ref', str(traffic_sign.related_obstacle))
            traffic_sign_node.append(related_obstacle_ref_node)
        
        return traffic_sign_node

    @classmethod
    def create_ref_node(cls, traffic_sign_ref) -> etree.Element:
        
        traffic_sign_ref_node = etree.Element('trafficSignRef')
        traffic_sign_ref_node.set('ref', str(traffic_sign_ref))
        return traffic_sign_ref_node
