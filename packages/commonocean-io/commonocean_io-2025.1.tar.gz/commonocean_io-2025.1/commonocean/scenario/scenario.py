from __future__ import annotations

import itertools
import re
import iso3166
from collections import defaultdict

from commonroad.common.util import Interval
from commonocean.prediction.prediction import Occupancy

from commonocean import SCENARIO_VERSION, SUPPORTED_COMMONOCEAN_VERSIONS
from commonocean.scenario.obstacle import StaticObstacle, DynamicObstacle, ObstacleRole, ObstacleType
from commonroad.scenario.state import State, CustomState

from commonocean.scenario.waters import *

from commonocean.visualization.drawable import IDrawable
from commonocean.visualization.param_server import ParamServer
from commonocean.visualization.renderer import IRenderer


# Tunneling from CR-IO #
from commonroad.scenario.scenario import GeoTransformation as GeoTransformation_CR
########################

__author__ = "Hanna Krasowski, Benedikt Pfleiderer, Fabian Thomas-Barein"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"


@enum.unique
class Tag(enum.Enum):
    """ Enum containing all possible tags of a CommonOcean scenario."""
    OPENSEA = "open_sea"
    TRAFFICSIGN = "traffic_sign"
    NARROWWATERS = "narrow_waters"
    TRAFFICSEPERATIONZONE = "traffic_separation_zone"
    HARBOUR = "harbour"
    COMFORT = "comfort"
    CRITICAL = "critical"
    EVASIVE = "evasive"
    SPEED_LIMIT = "speed_limit"


@enum.unique
class TimeOfDay(enum.Enum):
    """ Enum containing all possible time of days."""
    DAY = "day"
    NIGHT = "night"
    UNKNOWN = "unknown"


@enum.unique
class Weather(enum.Enum):
    """ Enum containing all possible weathers."""
    SUNNY = "sunny"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    FOG = "fog"
    SNOW = "snow"
    HAIL = "hail"
    UNKNOWN = "unknown"


@enum.unique
class SeaState(enum.Enum):
    """ Enum containing all possible sea states."""
    CALM = "calm"
    ROUGH = "rough"
    UNKNOWN = "unknown"


class Time:
    """
    Class which describes the fictive time when a scenario starts.
    """

    def __init__(self, year: int, month: int, day: int, hours: int, minutes: int):
        """
        Constructor of a time object

        :param year: year at start of scenario
        :param month: month at start of scenario (1-12)
        :param day: day at start of scenario (1-31)
        :param hours: hours at start of scenario (0-24)
        :param minutes: minutes at start of scenario (0-60)
        """
        self._year = year
        self._month = month
        self._day = day
        self._hours = hours
        self._minutes = minutes

    def __eq__(self, other):
        if not isinstance(other, Time):
            return False

        return (
            self._hours == other.hours
            and self._minutes == other.minutes
            and self._day == other.day
            and self._month == other.month
            and self._year == other.year
        )

    def __str__(self):
        return f"Year {self._year}, month {self._month}, day {self._day}, hour {self._hours}, minute {self.minutes}"

    def __hash__(self):
        return hash((self._hours, self._minutes, self._day, self._month, self._year))

    @property
    def hours(self) -> int:
        """Hours at start of scenario (0-24)"""
        return self._hours

    @hours.setter
    def hours(self, hours: int):
        self._hours = hours

    @property
    def minutes(self) -> int:
        """Minutes at start of scenario (0-60)"""
        return self._minutes

    @minutes.setter
    def minutes(self, minutes: int):
        self._minutes = minutes

    @property
    def day(self) -> Union[None, int]:
        """Day at start of scenario (1-31)"""
        return self._day

    @day.setter
    def day(self, day: Union[None, int]):
        self._day = day

    @property
    def month(self) -> Union[None, int]:
        """Month at start of scenario (1-12)"""
        return self._month

    @month.setter
    def month(self, month: Union[None, int]):
        self._month = month

    @property
    def year(self) -> Union[None, int]:
        """Year at start of scenario"""
        return self._year

    @year.setter
    def year(self, year: Union[None, int]):
        self._year = year


class GeoTransformation(GeoTransformation_CR):
    """
    Class which describes the transformation from geodetic to projected Cartesian coordinates according to the
    CommonOcean specification
    """

    def __init__(self, geo_reference: str = None, x_translation: float = None, y_translation: float = None,
                 z_rotation: float = None, scaling: float = None):
        """
        Constructor of a location object

        :param geo_reference: proj-string describing transformation from geodetic to projected Cartesian coordinates
        :param x_translation: translation value for x-coordinates
        :param y_translation: translation value for y-coordinates
        :param z_rotation: rotation value around origin
        :param scaling: multiplication value of x- and y-coordinates
        """
        super().__init__(geo_reference, x_translation, y_translation, z_rotation, scaling)

class Environment:
    """
    Class which describes the environment where a scenario takes place as specified in the CommonOcean specification.
    """

    def __init__(self, time: Time = None, time_of_day: TimeOfDay = None, weather: Weather = None,
                 seastate: SeaState = None):
        """
        Constructor of an environment object

        :param time: time when the scenario takes place
        :param time_of_day: time of day, e.g., day
        :param weather: weather information, e.g., sunny
        :param seastate: seastate information, e.g., calm
        """
        self._time = time
        self._time_of_day = time_of_day
        self._weather = weather
        self._seastate = seastate

    def __eq__(self, other):
        if not isinstance(other, Environment):
            return False

        return (
            self._time == other.time
            and self._time_of_day == other.time_of_day
            and self._weather == other.weather
            and self._seastate == other._seastate
        )


    def __hash__(self):
        return hash((self._time, self._time_of_day, self._weather, self._seastate))


    @property
    def time(self) -> Time:
        """Time when the scenario takes place"""
        return self._time

    @property
    def time_of_day(self) -> TimeOfDay:
        """Time of day, e.g., day"""
        return self._time_of_day

    @property
    def weather(self) -> Weather:
        """Weather information, e.g., sunny"""
        return self._weather

    @property
    def seastate(self) -> SeaState:
        """Seastate information, e.g., calm"""
        return self._seastate


class Location:
    """
    Class which describes a location according to the CommonRoad specification.
    """

    def __init__(
        self,
        geo_name_id: int = -999,
        gps_latitude: float = 999,
        gps_longitude: float = 999,
        geo_transformation: GeoTransformation = None,
        environment: Environment = None,
    ):
        """
        Constructor of a location object

        :param geo_name_id: GeoName ID
        :param gps_latitude: GPS latitude coordinate
        :param gps_longitude: GPS longitude coordinate
        :param geo_transformation: description of geometric transformation during scenario generation
        :param environment: environmental information, e.g. weather
        """
        self._geo_name_id = geo_name_id
        self._gps_latitude = gps_latitude
        self._gps_longitude = gps_longitude
        self._geo_transformation = geo_transformation
        self._environment = environment

    def __eq__(self, other):
        if not isinstance(other, Location):
            return False

        return (
            self._geo_name_id == other.geo_name_id
            and self._gps_latitude == other.gps_latitude
            and self._gps_longitude == other.gps_longitude
            and self._geo_transformation == other.geo_transformation
            and self._environment == other.environment
        )

    def __hash__(self):
        return hash(
            (self._geo_name_id, self._gps_latitude, self._gps_longitude, self._geo_transformation, self._environment)
        )

    @property
    def geo_name_id(self) -> int:
        """GeoName ID"""
        return self._geo_name_id

    @geo_name_id.setter
    def geo_name_id(self, geo_name_id: int):
        self._geo_name_id = geo_name_id

    @property
    def gps_latitude(self) -> float:
        """GPS latitude coordinate"""
        return self._gps_latitude

    @gps_latitude.setter
    def gps_latitude(self, gps_latitude: float):
        self._gps_latitude = gps_latitude

    @property
    def gps_longitude(self) -> float:
        """GPS longitude coordinate"""
        return self._gps_longitude

    @gps_longitude.setter
    def gps_longitude(self, gps_longitude: float):
        self._gps_longitude = gps_longitude

    @property
    def geo_transformation(self) -> GeoTransformation:
        """Description of geometric transformation during scenario generation"""
        return self._geo_transformation

    @geo_transformation.setter
    def geo_transformation(self, geo_transformation: GeoTransformation):
        self._geo_transformation = geo_transformation

    @property
    def environment(self) -> Environment:
        """Environmental information, e.g. weather"""
        return self._environment

    @environment.setter
    def environment(self, environment: Environment):
        self._environment = environment

#TODO - Update
class ScenarioID:
    def __init__(self, cooperative: bool = False, country_id: str = "ZAM", map_name: str = "Test", map_id: int = 1,
                 configuration_id: Union[None, int] = None, prediction_type: Union[None, str] = None,
                 prediction_id: Union[None, int] = None, scenario_version: str = SCENARIO_VERSION):
        """
        Implements the scenario ID as specified in the scenario documentation.
        Example for benchmark ID C-USA_US101-33_2_T-1
        :param cooperative: True if scenario contains cooperative planning problem sets with multiple planning problems
        :param country_id: three-letter ID according
        :param map_name: name of the map (e.g. US101)
        :param map_id: index of the map (e.g. 33)
        :param configuration_id: enumerates initial configuration of vehicles on the map (e.g. 2)
        :param prediction_type: type of the prediction for surrounding vehicles (e.g. T)
        :param prediction_id: enumerates different predictions for the same initial configuration (e.g. 1)
        :param scenario_version: scenario version identifier (e.g. 2020a)
        """
        assert scenario_version in SUPPORTED_COMMONOCEAN_VERSIONS, 'Scenario_version {} not supported.' \
            .format(scenario_version)
        self.scenario_version = scenario_version
        self.cooperative = cooperative
        self._country_id = None
        self.country_id = country_id
        self.map_name = map_name
        self.map_id = map_id
        self.configuration_id = configuration_id
        self.prediction_type = prediction_type
        self.prediction_id = prediction_id

    def __str__(self):
        scenario_id = ""
        if self.cooperative is True:
            scenario_id += "C-"
        if self.country_id is not None:
            scenario_id += self.country_id + "_"
        if self.map_name is not None:
            scenario_id += self.map_name + "-"
        if self.map_id is not None:
            scenario_id += str(self.map_id)
        if self.configuration_id is not None:
            scenario_id += "_" + str(self.configuration_id)
        if self.prediction_type is not None:
            scenario_id += "_" + self.prediction_type + "-"
        if self.prediction_id is not None:
            if type(self.prediction_id) == list:
                scenario_id += "-".join([str(i) for i in self.prediction_id])
            else:
                scenario_id += str(self.prediction_id)
        return scenario_id
        
    @property
    def country_id(self):
        """ Three-letter country ID according to ISO-3166."""
        return self._country_id

    @country_id.setter
    def country_id(self, country_id: str):
        if country_id is None:
            self._country_id = 'ZAM'
        elif country_id in iso3166.countries_by_alpha3 or country_id == 'ZAM':
            self._country_id = country_id
        else:
            raise ValueError('Country ID {} is not in the ISO-3166 three-letter format. '.format(country_id))

    @property
    def country_name(self):
        """ Name of the country according to the ISO-3166 standard."""
        if self.country_id == "ZAM":
            return "Zamunda"
        else:
            return iso3166.countries_by_alpha3[self.country_id].name

    @classmethod
    def from_benchmark_id(cls, benchmark_id: str, scenario_version: str) -> ScenarioID:
        """
        Create ScenarioID from benchmark_id and scenario_version in the XML header.

        :param benchmark_id: scenario ID provided as a string
        :param scenario_version: scenario format version (e.g. 2020a)
        :return: ScenarioID object
        """
        if not (benchmark_id.count('_') in (1, 2, 3) and benchmark_id.count('-') in (1, 2, 3, 4)):
            warnings.warn('Not a valid scenario id: ' + benchmark_id)
            return ScenarioID(None, None, benchmark_id, 0, None, None, None)

        
        if benchmark_id[0:2] == 'C-':
            cooperative = True
            benchmark_id = benchmark_id[2:]
        else:
            cooperative = False

        sub_ids = re.split('_|-', benchmark_id)
        country_id, map_name, map_id = sub_ids[:3]
        map_id = int(map_id)

        configuration_id = prediction_type = prediction_id = None
        if len(sub_ids) > 3:
            configuration_id = int(sub_ids[3])
        if len(sub_ids) > 4:
            assert sub_ids[4] in ('S', 'T', 'I'), "prediction type must be one of (S, T, I) but is {}".format(
                sub_ids[4])
            prediction_type = sub_ids[4]
            if len(sub_ids) == 6:
                prediction_id = int(sub_ids[5])
            else:
                prediction_id = [int(s) for s in sub_ids[5:]]

        return ScenarioID(cooperative, country_id, map_name, map_id, configuration_id, prediction_type, prediction_id,
                          scenario_version)

    def __eq__(self, other: 'ScenarioID'):
        return str(self) == str(other) and self.scenario_version == other.scenario_version

#TODO - Update
class Scenario(IDrawable):
    """ Class which describes a Scenario entity according to the CommonOcean specification. Each scenario is described by
     a ocean network consisting of waters (see :class:`commonocean.scenario.waters.WatersNetwork`) and a set of
     obstacles which can be either static or dynamic (see :class:`commonocean.scenario.obstacle.Obstacle`)."""

    def __init__(self, dt: float, scenario_id: Union[str, ScenarioID],
                 author: str = None, tags: Set[Tag] = None, affiliation: str = None, source: str = None,
                 location: Location = None, benchmark_id: str = None):
        """
        Constructor of a Scenario object

        :param dt: global time step size of the time-discrete scenario
        :param benchmark_id: unique CommonOcean benchmark ID of the scenario
        :param author: authors of the CommonOcean scenario
        :param tags: tags describing and classifying the scenario
        :param affiliation: institution of the authors
        :param source: source of the scenario, e.g. generated by a map converter and a traffic simulator
        :param location: location object of the scenario
        :param benchmark_id: for backwards compatibility
        """
        self.dt: float = dt
        self.scenario_id = scenario_id
        if isinstance(scenario_id, str):
            self.scenario_id = ScenarioID.from_benchmark_id(scenario_id, SCENARIO_VERSION)
        elif scenario_id is None and benchmark_id is not None:
            warnings.warn('Use the  the class commonocean.scenario.ScenarioID to define the scenario id.',
                          DeprecationWarning)
            self.scenario_id = ScenarioID.from_benchmark_id(benchmark_id,
                                                            SCENARIO_VERSION)

        self._waters_network: WatersNetwork = WatersNetwork(np.array([0,0]),0,0,0)

        self._static_obstacles: Dict[int, StaticObstacle] = defaultdict()
        self._dynamic_obstacles: Dict[int, DynamicObstacle] = defaultdict()

        self._id_set: Set[int] = set()
        
        # count ids generated but not necessarily added yet
        self._id_counter = None

        # meta data
        self.author = author
        self.tags = tags
        self.affiliation = affiliation
        self.source = source
        self.location = location

    @property
    def dt(self) -> float:
        """ Global time step size of the time-discrete scenario."""
        return self._dt

    @dt.setter
    def dt(self, dt: float):
        assert is_real_number(dt), '<Scenario/dt> argument "dt" of wrong type. ' \
                                   'Expected a real number. Got type: %s.' % type(dt)
        self._dt = dt

    @property
    def benchmark_id(self) -> str:
        """ Unique benchmark ID of a scenario as specified in the CommonOcean XML-file."""
        warnings.warn('benchmark_id is deprecated, use scenario_id instead', DeprecationWarning)
        return str(self.scenario_id)

    @benchmark_id.setter
    def benchmark_id(self, benchmark_id):
        raise ValueError('benchmark_id is deprecated, use scenario_id instead')

    @property
    def waters_network(self) -> WatersNetwork:
        """ WatersNetwork of the scenario."""
        raise ValueError("You are trying to access the WatersNetwork of your scenario. This is not recommended, to avoid future bugs in your work! To alter your Network, use the appropriate method scenario.add_objects(). If it is really unavoidable to access the WatersNetwork object of your Scenario, use scenario._waters_network.")

    @property
    def dynamic_obstacles(self) -> List[DynamicObstacle]:
        """ Returns a list of all dynamic obstacles in the scenario."""
        return list(self._dynamic_obstacles.values())

    @property
    def static_obstacles(self) -> List[StaticObstacle]:
        """ Returns a list of all static obstacles in the scenario."""
        return list(self._static_obstacles.values())

    @property
    def obstacles(self) -> List[Union[Obstacle, StaticObstacle, DynamicObstacle]]:
        """ Returns a list of all static and dynamic obstacles in the scenario."""
        return list(itertools.chain(self._static_obstacles.values(),
                                    self._dynamic_obstacles.values()))

    def add_objects(self, scenario_object: Union[List[Union[Obstacle, Waters, WatersNetwork, TrafficSign]], Obstacle, Waters, WatersNetwork,
                                                 TrafficSign], waters_ids: Union[None, Set[int]] = None, traffic_sign_parameters: Dict[str, Any] = None):
        """ Function to add objects, e.g., waters, dynamic and static obstacles, to the scenario.

            :param scenario_object: object(s) to be added to the scenario
            :param waters_ids: water IDs a traffic sign should be referenced from
            :param traffic_sign_parameters: dict of parameters of the obstacle related with the traffic sign (keys must be 'obstacle_type', 'obstacle_id' and 'radius')
            :raise ValueError: a value error is raised if the type of scenario_object is invalid.
        """
        if isinstance(scenario_object, list):
            for obj in scenario_object:
                self.add_objects(obj)
        elif isinstance(scenario_object, StaticObstacle):
            self._mark_object_id_as_used(scenario_object.obstacle_id)
            self._static_obstacles[scenario_object.obstacle_id] = scenario_object
        elif isinstance(scenario_object, DynamicObstacle):
            self._mark_object_id_as_used(scenario_object.obstacle_id)
            self._dynamic_obstacles[scenario_object.obstacle_id] = scenario_object
        elif isinstance(scenario_object, WatersNetwork):
            for water in scenario_object.waters:
                self._mark_object_id_as_used(water.waters_id)
            for traffic_sign in scenario_object.traffic_signs:
                self._mark_object_id_as_used(traffic_sign.traffic_sign_id)
            for shallow in scenario_object.shallows:
                self._mark_object_id_as_used(shallow.waters_id)
            self._waters_network: WatersNetwork = scenario_object
            warnings.warn('WatersNetwork replaced. (When a WatersNetwork is used in the add_objects method, the old one present in the scenario is replaced by the new one)')
        elif isinstance(scenario_object, Waters):
            self._mark_object_id_as_used(scenario_object.waters_id)
            self._waters_network.add_waters(scenario_object)
        elif isinstance(scenario_object, TrafficSign):
            warnings.warn('By adding a traffic sign, you automatically creates an obstacle in the same position that represent the physical boundary of the sign.')
            self._mark_object_id_as_used(scenario_object.traffic_sign_id)
            self._waters_network.add_traffic_sign(scenario_object, waters_ids)
            if traffic_sign_parameters is None:
                traffic_sign_parameters = {'obstacle_type': ObstacleType.BUOY, 'obstacle_id': self.generate_object_id(), 'radius': 5}
            else:
                pass
            obstacle_type = traffic_sign_parameters.get('obstacle_type', ObstacleType.BUOY)
            obstacle_id = traffic_sign_parameters.get('obstacle_id', None)
            obstacle_radius = traffic_sign_parameters.get('radius', 5)
            if obstacle_id is None:
                obstacle_id = self.generate_object_id()
            else:
                pass
            position = scenario_object.position
            above_obstacle_list = self.obstacles_by_position_intervals(position_intervals=[Interval(start=position[0] - obstacle_radius, end=position[0] + obstacle_radius), Interval(start= position[1] - obstacle_radius, end=position[1] + obstacle_radius)], obstacle_role=[ObstacleRole.STATIC])
            if above_obstacle_list:
                obstacle_id = above_obstacle_list[0].obstacle_id
                warnings.warn('As there was already an obstacle under the position of your traffic_sign, a new obstacle was not inserted!')
            else:
                circ_1 = Circle(obstacle_radius)
                init_state_1 = CustomState(time_step=0, orientation=0, position=position, velocity=0)
                static_obs_1 = StaticObstacle(obstacle_id, obstacle_type, obstacle_shape=circ_1, initial_state=init_state_1)
                self._mark_object_id_as_used(obstacle_id)
                self._static_obstacles[obstacle_id] = static_obs_1
            scenario_object.related_obstacle = obstacle_id
       
        else:
            raise ValueError('<Scenario/add_objects> argument "scenario_object" of wrong type. '
                             'Expected types: %s, %s, %s, and %s. Got type: %s.'
                             % (list, Obstacle, Waters, WatersNetwork, type(scenario_object)))

    def remove_obstacle(self, obstacle: Union[Obstacle, List[Obstacle]]):
        """ Removes a static, dynamic or a list of obstacles from the scenario. If the obstacle ID is not assigned,
        a warning message is given.

        :param obstacle: obstacle to be removed
        """
        assert isinstance(obstacle, (list, Obstacle)), '<Scenario/remove_obstacle> argument "obstacle" of wrong type. ' \
                                                       'Expected type: %s. Got type: %s.' % (Obstacle, type(obstacle))
        if isinstance(obstacle, list):
            for obs in obstacle:
                self.remove_obstacle(obs)
            return

        if obstacle.obstacle_id in self._static_obstacles:
            del self._static_obstacles[obstacle.obstacle_id]
            self._id_set.remove(obstacle.obstacle_id)
        elif obstacle.obstacle_id in self._dynamic_obstacles:
            del self._dynamic_obstacles[obstacle.obstacle_id]
            self._id_set.remove(obstacle.obstacle_id)
        else:
            warnings.warn('<Scenario/remove_obstacle> Cannot remove obstacle with ID %s, '
                          'since it is not contained in the scenario.' % obstacle.obstacle_id)

    def erase_waters_network(self):
        """
        Removes all elements from waters network.
        """
        for waters in self._waters_network.waters:
            self.remove_waters(waters)
        for traffic_sign in self._waters_network.traffic_signs:
            self.remove_traffic_sign(traffic_sign)
        self._waters_network = WatersNetwork(np.array([0,0]),0,0,0)

    def replace_waters_network(self, waters_network: WatersNetwork):
        """
        Removes waters network with all its elements from the scenario and replaces it with new waters network.

        :param waters_network: new waters network
        """
        self.erase_waters_network()
        self.add_objects(waters_network)

    def remove_hanging_waters_members(self, remove_waters: Union[List[Waters], Waters]):
        """
        After removing waters from remove_waters, this function removes all traffic lights and signs that are
        not used by other waters.

        :param remove_waters: Waters that should be removed from scenario.
        """
        all_waters = self._waters_network.waters
        remove_waters_ids = [la.waters_id for la in remove_waters]
        remaining_waters = [la for la in all_waters if la.waters_id not in remove_waters_ids]

        traffic_signs_to_delete = set().union(*[la.traffic_signs for la in remove_waters])
        traffic_signs_to_save = set().union(*[la.traffic_signs for la in remaining_waters])

        remove_traffic_signs = []

        for t in self._waters_network.traffic_signs:
            if t.traffic_sign_id in set(traffic_signs_to_delete - traffic_signs_to_save):
                remove_traffic_signs.append(self._waters_network.find_traffic_sign_by_id(t.traffic_sign_id))

        self.remove_traffic_sign(remove_traffic_signs)

    def remove_waters(self, waters: Union[List[Waters], Waters], referenced_elements: bool = True):
        """
        Removes a waters or a list of waters from a scenario.

        :param waters: Waters which should be removed from scenario.

        :param referenced_elements: Boolean indicating whether references of waters should also be removed.
        """
        assert isinstance(waters, (list, Waters)), '<Scenario/remove_waters> argument "waters" of wrong type. ' \
                                                     'Expected type: %s. Got type: %s.' % (Waters, type(waters))
        assert isinstance(referenced_elements,
                          bool), '<Scenario/remove_waters> argument "referenced_elements" of wrong type. ' \
                                 'Expected type: %s, Got type: %s.' % (bool, type(referenced_elements))
        if not isinstance(waters, list):
            waters = [waters]

        if referenced_elements:
            self.remove_hanging_waters_members(waters)

        for la in waters:
            self._waters_network.remove_waters(la.waters_id)
            self._id_set.remove(la.waters_id)

    def remove_traffic_sign(self, traffic_sign: Union[List[TrafficSign], TrafficSign]):
        """
        Removes a traffic sign or a list of traffic signs from the scenario.

        :param traffic_sign: Traffic sign which should be removed from scenario.
        """
        assert isinstance(traffic_sign,
                          (list, TrafficSign)), '<Scenario/remove_traffic_sign> argument "traffic_sign" of wrong ' \
                                                'type. ' \
                                                'Expected type: %s. Got type: %s.' % (TrafficSign, type(traffic_sign))
        if isinstance(traffic_sign, list):
            for sign in traffic_sign:
                self._waters_network.remove_traffic_sign(sign.traffic_sign_id)
                self._id_set.remove(sign.traffic_sign_id)
                self.remove_obstacle(self.obstacle_by_id(sign.related_obstacle))
            return

        self._waters_network.remove_traffic_sign(traffic_sign.traffic_sign_id)
        self._id_set.remove(traffic_sign.traffic_sign_id)
        self.remove_obstacle(self.obstacle_by_id(traffic_sign.related_obstacle))

    def generate_object_id(self) -> int:
        """ Generates a unique ID which is not assigned to any object in the scenario.

            :return: unique object ID
        """
        if self._id_counter is None:
            self._id_counter = 0
        if len(self._id_set) > 0:
            max_id_used = max(self._id_set)
            self._id_counter = max(self._id_counter, max_id_used)
        self._id_counter += 1
        return int(self._id_counter)

    @property
    def shallows(self) -> List[Shallow]:
        """ Returns a list of all shallows in the WatersNetwork of the scenario."""
        return self._waters_network.shallows
    
    @property
    def waterways(self) -> List[Waterway]:
        """ Returns a list of all waterways in the WatersNetwork of the scenario."""
        return self._waters_network.waterways
    
    @property
    def waters(self) -> List[Waters]:
        """ Returns a list of all waters (waterways and shallows) in the WatersNetwork of the scenario."""
        return self._waters_network.waters

    def occupancies_at_time_step(self, time_step: int, obstacle_role: Union[None, ObstacleRole] = None) \
            -> List[Occupancy]:
        """ Returns the occupancies of all static and dynamic obstacles at a specific time step.

            :param time_step: occupancies of obstacles at this time step
            :param obstacle_role: obstacle role as defined in CommonOcean, e.g., static or dynamic
            :return: list of occupancies of the obstacles
        """
        assert is_natural_number(time_step), '<Scenario/occupancies_at_time> argument "time_step" of wrong type. ' \
                                             'Expected type: %s. Got type: %s.' % (int, type(time_step))
        assert isinstance(obstacle_role, (ObstacleRole, type(None))), \
            '<Scenario/obstacles_by_role_and_type> argument "obstacle_role" of wrong type. Expected types: ' \
            ' %s or %s. Got type: %s.' % (ObstacleRole, None, type(obstacle_role))
        occupancies = list()
        for obstacle in self.obstacles:
            if ((obstacle_role is None or obstacle.obstacle_role == obstacle_role) and
                    obstacle.occupancy_at_time(time_step)):
                occupancies.append(obstacle.occupancy_at_time(time_step))
        return occupancies

    def obstacle_by_id(self, obstacle_id: int) -> Union[Obstacle, DynamicObstacle, StaticObstacle, None]:
        """
        Finds an obstacle for a given obstacle_id

        :param obstacle_id: ID of the queried obstacle
        :return: the obstacle object if the ID exists, otherwise None
        """
        assert is_integer_number(obstacle_id), '<Scenario/obstacle_by_id> argument "obstacle_id" of wrong type. ' \
                                               'Expected type: %s. Got type: %s.' % (int, type(obstacle_id))
        obstacle = None
        if obstacle_id in self._static_obstacles:
            obstacle = self._static_obstacles[obstacle_id]
        elif obstacle_id in self._dynamic_obstacles:
            obstacle = self._dynamic_obstacles[obstacle_id]
        else:
            warnings.warn('<Scenario/obstacle_by_id> Obstacle with ID %s is not contained in the scenario.'
                          % obstacle_id)
        return obstacle

    def obstacles_by_role_and_type(self, obstacle_role: Union[None, ObstacleRole] = None,
                                   obstacle_type: Union[None, ObstacleType] = None) \
            -> List[Obstacle]:
        """
        Filters the obstacles by their role and type.

        :param obstacle_role: obstacle role as defined in CommonOcean, e.g., static or dynamic
        :param obstacle_type: obstacle type as defined in CommonOcean, e.g., car, train, or bus
        :return: list of all obstacles satisfying the given obstacle_role and obstacle_type
        """
        assert isinstance(obstacle_role, (ObstacleRole, type(None))), \
            '<Scenario/obstacles_by_role_and_type> argument "obstacle_role" of wrong type. Expected types: ' \
            ' %s or %s. Got type: %s.' % (ObstacleRole, None, type(obstacle_role))
        assert isinstance(obstacle_type, (ObstacleType, type(None))), \
            '<Scenario/obstacles_by_role_and_type> argument "obstacle_type" of wrong type. Expected types: ' \
            ' %s or %s. Got type: %s.' % (ObstacleType, None, type(obstacle_type))
        obstacle_list = list()
        for obstacle in self.obstacles:
            if ((obstacle_role is None or obstacle.obstacle_role == obstacle_role)
                    and (obstacle_type is None or obstacle.obstacle_type == obstacle_type)):
                obstacle_list.append(obstacle)
        return obstacle_list

    def obstacles_by_position_intervals(
            self, position_intervals: List[Interval],
            obstacle_role: Tuple[ObstacleRole] = (ObstacleRole.DYNAMIC, ObstacleRole.STATIC),
            time_step: int = None) -> List[Obstacle]:
        """
        Returns obstacles which center is located within in the given x-/y-position intervals.

        :param position_intervals: list of intervals for x- and y-coordinates [interval_x,  interval_y]
        :param obstacle_role: tuple containing the desired obstacle roles
        :return: list of obstacles in the position intervals
        """

        def contained_in_interval(position: np.ndarray):
            if position_intervals[0].contains(position[0]) and position_intervals[1].contains(position[1]):
                return True
            return False

        if time_step is None:
            time_step = 0

        obstacle_list = list()
        if ObstacleRole.STATIC in obstacle_role:
            for obstacle in self.static_obstacles:
                if contained_in_interval(obstacle.initial_state.position):
                    obstacle_list.append(obstacle)
        if ObstacleRole.DYNAMIC in obstacle_role:
            for obstacle in self.dynamic_obstacles:
                occ = obstacle.occupancy_at_time(time_step)
                if occ is not None:
                    if not hasattr(occ.shape, 'center'):
                        obstacle_list.append(obstacle)
                    elif contained_in_interval(occ.shape.center):
                        obstacle_list.append(obstacle)
        return obstacle_list

    def obstacle_states_at_time_step(self, time_step: int) -> Dict[int, State]:
        """
        Returns all obstacle states which exist at a provided time step.

        :param time_step: time step of interest
        :return: dictionary which maps id to obstacle state at time step
        """
        assert is_natural_number(time_step), '<Scenario/obstacle_at_time_step> argument "time_step" of wrong type. ' \
                                             'Expected type: %s. Got type: %s.' % (int, type(time_step))

        obstacle_states = {}
        for obstacle in self.dynamic_obstacles:
            if obstacle.state_at_time(time_step) is not None:
                obstacle_states[obstacle.obstacle_id] = obstacle.state_at_time(time_step)
        for obstacle in self.static_obstacles:
            obstacle_states[obstacle.obstacle_id] = obstacle.initial_state
        return obstacle_states
        
    def translate_rotate(self, translation: np.ndarray, angle: float):
        """ Translates and rotates all objects, e.g., obstacles and water network, in the scenario.

            :param translation: translation vector [x_off, y_off] in x- and y-direction
            :param angle: rotation angle in radian (counter-clockwise)
        """
        assert is_real_number_vector(translation, 2), '<Scenario/translate_rotate>: argument "translation" is ' \
                                                      'not a vector of real numbers of length 2. translation = {}.' \
            .format(translation)
        assert is_valid_orientation(angle), '<Scenario/translate_rotate>: argument "orientation" is not valid. ' \
                                            'angle = {}.'.format(angle)

        self._waters_network.translate_rotate(translation, angle)
        for obstacle in self.obstacles:
            obstacle.translate_rotate(translation, angle)

    def _is_object_id_used(self, object_id: int) -> bool:
        """ Checks if an ID is already assigned to an object in the scenario.

            :param object_id: object ID to be checked
            :return: True, if the object ID is already assigned, False otherwise
        """
        return object_id in self._id_set

    def _mark_object_id_as_used(self, object_id: int):
        """ Checks if an ID is assigned to an object in the scenario. If the ID is already assigned an error is
        raised, otherwise, the ID is added to the set of assigned IDs.

        :param object_id: object ID to be checked
        :raise ValueError:  if the object ID is already assigned to another object in the scenario.
        """
        if self._id_counter is None:
            self._id_counter = object_id
        if self._is_object_id_used(object_id):
            raise ValueError("ID %s is already used." % object_id)
        self._id_set.add(object_id)

    def __str__(self):
        traffic_str = "\n"
        traffic_str += "Scenario:\n"
        traffic_str += "- Scenario ID: {}\n".format(str(self.scenario_id))
        traffic_str += "- Time step size: {}\n".format(self._dt)
        traffic_str += "- Number of Obstacles: {}\n".format(len(self.obstacles))
        traffic_str += "- WatersNetwork:\n"
        traffic_str += str(self._waters_network)
        return traffic_str

    def draw(self, renderer: IRenderer,
             draw_params: Union[ParamServer, dict, None] = None):
        renderer.draw_scenario(self, draw_params)

