import math
import os
import platform
import re
import subprocess
from xml.dom import minidom
import numpy as np
import xml.etree.ElementTree as et
from enum import Enum, unique
from typing import List, Tuple, Union, Dict
from datetime import datetime
import vesselmodels.parameters_vessel_1 as p1
import vesselmodels.parameters_vessel_2 as p2
import vesselmodels.parameters_vessel_3 as p3

from commonroad.common.validity import is_real_number, is_positive
from commonroad.geometry.shape import Rectangle

from commonocean.prediction.prediction import TrajectoryPrediction
from commonocean.scenario.obstacle import DynamicObstacle, ObstacleType
from commonocean.scenario.scenario import ScenarioID
from commonocean.scenario.trajectory import Trajectory
from commonroad.scenario.state import State, CustomState

# Tunneling from CR-IO #
from commonroad.common.solution import SolutionException, StateTypeException, SolutionReaderException
########################

__author__ = "Bruno Maione, Hanna Krasowski"
__copyright__ = "TUM Cyber-Physical Systems Group"
__credits__ = ""
__version__ = "2022.1"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "Released"


@unique
class VesselType(Enum):
    Vessel1 = 1
    Vessel2 = 2
    Vessel3 = 3


vessel_parameters = {VesselType.Vessel1: p1.parameters_vessel_1(),
                      VesselType.Vessel2: p2.parameters_vessel_2(),
                      VesselType.Vessel3: p3.parameters_vessel_3()}


@unique
class VesselModel(Enum):
    PM = 0
    VP = 1
    YP = 2
    TF = 3

@unique
class CostFunction(Enum):
    JB1 = 0
    VRCO1 = 1
    RC1 = 2
    SB1 = 3

@unique
class StateFields(Enum):
    """
    State Fields enum class for defining the state fields for vessel models for different trajectory types.

    PM | VP | YP | TF -> Corresponding state fields for trajectory states
    __Name__Input     -> Input fields for correspondent vessel models

    Note: If you change the order of field names, don't forget to change the order on the XMLStateFields enum as well,
    because the indexes have to match.
    """
    PMVP = ['position', 'velocity', 'velocity_y', 'time_step']
    PMVPInput = ['acceleration', 'acceleration_y', 'time_step']

    YP = ['position', 'orientation', 'velocity', 'time_step']
    YPInput = ['acceleration', 'yaw_rate', 'time_step']

    TF = ['position', 'orientation', 'velocity', 'velocity_y', 'yaw_rate', 'time_step']
    TFInput = ['force_orientation','force_lateral','yaw_moment', 'time_step']



@unique
class XMLStateFields(Enum):
    """
    XML names of the state fields for vessel models for different trajectory types.

    PM | VP | YP | TF  -> Corresponding xml names of the state fields for trajectory states
    __Name__Input      -> XML names of the input fields for correspondent vessel models.

    Note: If you change the order of xml names, don't forget to change the order on the StateFields enum as well,
    because the indexes have to match.
    """
    PMVP = [('x', 'y'), 'xVelocityFront', 'yVelocityFront', 'time']
    PMVPInput = ['xAcceleration', 'yAcceleration', 'time']

    YP = [('x', 'y'), 'orientation', 'xVelocityFront', 'time']
    YPInput = ['xAcceleration', 'yawRate', 'time']

    TF = [('x', 'y'), 'orientation', 'xVelocityFront', 'yVelocityFront', 'yawRate', 'time']
    TFInput = ['forceOrientation', 'forceLateral', 'yawMoment', 'time']
    


@unique
class StateType(Enum):
    """
    State Type enum class.

    PM | YP | TF  -> Corresponding state type for trajectory states
    __Name__Input      -> Input type correspondent vessel models
    """

    PMVP = 'pmState'
    YP = 'ypState'
    TF = 'tfState'

    PMVPInput = 'PMVPInput'
    YPInput = 'YPInput'
    TFInput = 'TFInput'    

    @property
    def fields(self) -> List[str]:
        """
        Returns the state fields for the state type.

        :return: State fields as list
        """
        return StateFields[self.name].value

    @property
    def xml_fields(self) -> List[str]:
        """
        Returns the xml state fields for the state type.

        :return: XML names of the state fields as list
        """
        return XMLStateFields[self.name].value

    @classmethod
    def get_state_type(cls, state: State, desired_vessel_model: VesselModel = None) -> 'StateType':
        """
        Returns the corresponding StateType for the given State object by matching State object's attributes
        to the state fields.

        :param state: CommonOcean State object
        :param desired_vessel_model: check if given vessel_model is supported first
        :return: corresponding StateType
        """
        # put desired_vessel_model first
        attrs = state.attributes
        
        if desired_vessel_model.name == 'PM' or desired_vessel_model.name == 'VP':
            search_name = 'PMVP'
        else:
            search_name = str(desired_vessel_model.name)

        if desired_vessel_model is not None:
            state_fields_all = [StateFields[search_name], StateFields.YPInput, StateFields.TFInput, StateFields.PMVPInput]
            state_fields_add = []
            for sf in StateFields:
                if sf not in state_fields_all:
                    state_fields_add.append(sf)

            state_fields_all += state_fields_add

            for state_fields in state_fields_all:
                if not len(attrs) >= len(state_fields.value):
                    continue  # >=
                if not all([sf in attrs for sf in state_fields.value]):
                    continue
                return cls[state_fields.name]
        else:
            state_fields_all = StateFields
            for state_fields in state_fields_all:
                if not len(attrs) == len(state_fields.value):
                    continue  # ==
                if not all([sf in attrs for sf in state_fields.value]):
                    continue
                return cls[state_fields.name]

        raise StateTypeException('Given state is not valid!')

    @classmethod
    def check_state_type(cls, vessel_model: VesselModel) -> None:
        """
        Checks whether vessel model can be supported by trajectory.
        :param vessel_model: vessel model enum
        :return: bool
        """
        StateFields(vessel_model.name)


@unique
class TrajectoryType(Enum):
    """
    Trajectory Type enum class.

    PM | VP | YP | TF  -> Corresponding trajectory type for the vessel models
    __Name__Input      -> InputVector type for PM, VP, YP and TF vessel models
    """
    PMVP = 'pmvpTrajectory'
    PMVPInput = 'PMVPInputVector'

    YP = 'ypTrajectory'
    YPInput = 'YPInputVector'

    TF = 'tfTrajectory'
    TFInput = 'TFInputVector'


    @property
    def state_type(self) -> StateType:
        """
        Returns the StateType corresponding to the TrajectoryType

        :return: StateType
        """
        return StateType[self.name]

    @classmethod
    def get_trajectory_type(cls, trajectory: Trajectory,
                            desired_vessel_model: VesselModel = None) -> 'TrajectoryType':
        """
        Returns the corresponding TrajectoryType for the given Trajectory object based on the StateType of its states.

        :param trajectory: CommonOcean Trajectory object
        :param desired_vessel_model: check if given vessel_model is supported first
        :return: corresponding TrajectoryType
        """
        state_type = StateType.get_state_type(trajectory.state_list[0], desired_vessel_model)
        return cls[state_type.name]

    def valid_vessel_model(self, vessel_model: VesselModel) -> bool:
        """
        Checks whether given vessel model is valid for the TrajectoryType.

        :param vessel_model: CommonOcean enum for vessel models
        :return: True if the vessel model is valid for the TrajectoryType
        """
        return any([
            self.name == 'PMVP' and vessel_model == VesselModel.PM,
            self.name == 'PMVP' and vessel_model == VesselModel.VP,
            self.name == 'YP' and vessel_model == VesselModel.YP,
            self.name == 'TF' and vessel_model == VesselModel.TF,
            self.name == 'PMVPInput' and vessel_model == VesselModel.PM,
            self.name == 'PMVPInput' and vessel_model == VesselModel.VP,
            self.name == 'YPInput' and vessel_model == VesselModel.YP,
            self.name == 'TFInput' and vessel_model == VesselModel.TF,
            self.name == vessel_model.name
        ])


class SupportedCostFunctions(Enum):
    """
    Enum class for specifying which cost functions are supported for which vessel model
    """
    PM = [cost_function for cost_function in CostFunction]  # Supports all cost functions
    VP = [cost_function for cost_function in CostFunction]  # Supports all cost functions
    YP = [cost_function for cost_function in CostFunction]  # Supports all cost functions
    TF = [cost_function for cost_function in CostFunction]  # Supports all cost functions

class PlanningProblemSolution:
    def __init__(self,
                 planning_problem_id: int,
                 vessel_model: VesselModel,
                 vessel_type: VesselType,
                 cost_function: CostFunction,
                 trajectory: Trajectory):
        """
        Constructor for the PlanningProblemSolution class.

        :param planning_problem_id: ID of the planning problem
        :param vessel_model: VesselModel used for the solution
        :param vessel_type: VesselType used for the solution
        :param cost_function: CostFunction the solution will be evaluated with
        :param trajectory: Ego vessel's trajectory for the solution.
        """

        self.planning_problem_id = planning_problem_id
        self._vessel_model = vessel_model
        self.vessel_type = vessel_type
        self._cost_function = cost_function
        self._trajectory = trajectory
        self._trajectory_type = TrajectoryType.get_trajectory_type(self._trajectory, self.vessel_model)

        self._check_trajectory_supported(self._vessel_model, self._trajectory_type)
        self._check_cost_supported(self._vessel_model, self._cost_function)

    @staticmethod
    def _check_cost_supported(vessel_model: VesselModel, cost_function: CostFunction) -> bool:
        """
        Checks whether given cost function is supported by the given vessel model.

        :param vessel_model: VesselModel
        :param cost_function: CostFunction
        :return: True if supported.
        """
        supported_costs = SupportedCostFunctions[vessel_model.name].value
        if cost_function not in supported_costs:
            raise SolutionException("Cost function %s isn't supported for %s model!" % (cost_function.name,
                                                                                        vessel_model.name))
        return True

    def _check_trajectory_supported(self, vessel_model: VesselModel, trajectory_type: TrajectoryType) -> bool:
        """
        Checks whether given vessel model is valid for the given trajectory type.

        :param vessel_model: VesselModel
        :param trajectory_type: TrajectoryType
        :return: True if valid.
        """

        ######################## ATTENTION ########################
        if self._vessel_model == VesselModel.PM and self._trajectory_type == TrajectoryType.PMVP:
            for state in self._trajectory.state_list:
                if not hasattr(state, 'orientation'):
                    state.orientation = math.atan2(state.velocity_y, state.velocity)
        
        if self._vessel_model == VesselModel.VP and self._trajectory_type == TrajectoryType.PMVP:
            for state in self._trajectory.state_list:
                if not hasattr(state, 'orientation'):
                    state.orientation = math.atan2(state.velocity_y, state.velocity)
        ######################## ATTENTION ########################

        if not trajectory_type.valid_vessel_model(vessel_model):
            raise SolutionException('Vessel model %s is not valid for the trajectory type %s!'
                                    % (vessel_model.name, trajectory_type.name))
        return True

    @property
    def vessel_model(self) -> VesselModel:
        """ VesselModel of the PlanningProblemSolution """
        return self._vessel_model

    @vessel_model.setter
    def vessel_model(self, vessel_model: VesselModel):
        self._check_trajectory_supported(vessel_model, self._trajectory_type)
        self._check_cost_supported(vessel_model, self.cost_function)

        self._vessel_model = vessel_model

    @property
    def cost_function(self) -> CostFunction:
        """ CostFunction of the PlanningProblemSolution """
        return self._cost_function

    @cost_function.setter
    def cost_function(self, cost_function: CostFunction):
        self._check_cost_supported(self.vessel_model, cost_function)
        self._cost_function = cost_function

    @property
    def trajectory(self) -> Trajectory:
        """ Trajectory of the PlanningProblemSolution """
        return self._trajectory

    @trajectory.setter
    def trajectory(self, trajectory: Trajectory):
        trajectory_type = TrajectoryType.get_trajectory_type(trajectory)
        self._check_trajectory_supported(self.vessel_model, trajectory_type)

        self._trajectory = trajectory
        self._trajectory_type = trajectory_type

    @property
    def trajectory_type(self) -> TrajectoryType:
        """
        TrajectoryType of the PlanningProblemSolution.
        Dynamically assigned when there is a change of trajectory.
        """
        return self._trajectory_type

    @property
    def vessel_id(self) -> str:
        """
        Returns the Vessel id as string.

        Example:
            VesselModel = VP
            VesselType = Vessel1
            Vessel ID = VP1

        :return: vessel model ID
        """
        return self.vessel_model.name + str(self.vessel_type.value)

    @property
    def cost_id(self) -> str:
        """
        Returns cost function id as str.

        Example:
            CostFunction = JB1
            Cost ID = JB1

        :return: Cost function ID
        """
        return self.cost_function.name


class Solution:
    """Stores a solution to a CommonOcean benchmark and additional meta data."""

    def __init__(self,
                 scenario_id: ScenarioID,
                 planning_problem_solutions: List[PlanningProblemSolution],
                 date: datetime = datetime.today(),
                 computation_time: Union[float, None] = None,
                 processor_name: Union[str, None] = None):
        """
        :param scenario_id: Scenario ID of the Solution
        :param planning_problem_solutions: List of PlanningProblemSolution for corresponding
            to the planning problems of the scenario
        :param date: The date solution was produced. Default=datetime.today()
        :param computation_time: The computation time measured in seconds for the Solution. Default=None
        :param processor_name: The processor model used for the Solution. Determined automatically if set to 'auto'.
            Default=None.
        """
        self.scenario_id = scenario_id
        self._planning_problem_solutions: Dict[int, PlanningProblemSolution] = {}
        self.planning_problem_solutions = planning_problem_solutions
        self.date = date
        self._computation_time = None
        self.computation_time = computation_time
        self.processor_name = processor_name

    @property
    def planning_problem_solutions(self) -> List[PlanningProblemSolution]:
        """ List of planning problem solutions """
        return list(self._planning_problem_solutions.values())

    @planning_problem_solutions.setter
    def planning_problem_solutions(self, planning_problem_solutions: List[PlanningProblemSolution]):
        self._planning_problem_solutions = {s.planning_problem_id: s for s in planning_problem_solutions}

    @property
    def benchmark_id(self) -> str:
        """
        Returns the benchmark id of the solution as string.

        Example:
            Scenario ID = TEYP
            VesselModel = VP
            VesselType = Vessel1
            CostFunction = JB1
            Version = 2022a

            Benchmark ID = VP1:JB1:TEYP:2022a

        Collaborative Solution Example:
            Scenario ID = TEYP
            1st VesselModel = VP
            1st VesselType = Vessel1
            1st CostFunction = JB1
            2nd VesselModel = PM
            2nd VesselType = Vessel3
            2nd CostFunction = RC1
            Version = 2020a

            Benchmark ID = [VP1,PM3]:[JB1,RC1]:TEYP:2020a

        :return: Benchmark ID
        """
        vessels_ids = self.vessels_ids
        cost_ids = self.cost_ids
        vessels_str = vessels_ids[0] if len(vessels_ids) == 1 else '[%s]' % ','.join(vessels_ids)
        costs_str = cost_ids[0] if len(cost_ids) == 1 else '[%s]' % ','.join(cost_ids)
        return '%s:%s:%s:%s' % (vessels_str, costs_str, str(self.scenario_id), self.scenario_id.scenario_version)

    @property
    def vessels_ids(self) -> List[str]:
        """
        Returns the list of vessel ids of all PlanningProblemSolutions of the Solution

        Example:
            1st PlanningProblemSolution Vessel ID = VP1
            2nd PlanningProblemSolution Vessel ID = VP3

            Vessel IDS = [VP1, VP3]

        :return: List of vessel IDs
        """
        return [pp_solution.vessel_id for pp_solution in self.planning_problem_solutions]

    @property
    def cost_ids(self) -> List[str]:
        """
        Returns the list of cost ids of all PlanningProblemSolutions of the Solution

        Example:
            1st PlanningProblemSolution Cost ID = JB1
            2nd PlanningProblemSolution Cost ID = RC1

            Cost IDS = [JB1, RC1]

        :return: List of cost function IDs
        """
        return [pp_solution.cost_id for pp_solution in self.planning_problem_solutions]

    @property
    def planning_problem_ids(self) -> List[int]:
        """
        Returns the list of planning problem ids of all PlanningProblemSolutions of the Solution

        Example:
            1st PlanningProblemSolution planning_problem_id = 0
            2nd PlanningProblemSolution planning_problem_id = 1

            planning_problem_ids = [0, 1]

        :return: List of planning problem ids
        """
        return [pp_solution.planning_problem_id for pp_solution in self.planning_problem_solutions]

    @property
    def trajectory_types(self) -> List[TrajectoryType]:
        """
        Returns the list of trajectory types of all PlanningProblemSolutions of the Solution

        Example:
            1st PlanningProblemSolution trajectory_type = TrajectoryType.VP
            2nd PlanningProblemSolution trajectory_type = TrajectoryType.TF

            trajectory_types = [TrajectoryType.VP, TrajectoryType.TF]

        :return: List of trajectory types
        """
        return [pp_solution.trajectory_type for pp_solution in self.planning_problem_solutions]

    @property
    def computation_time(self) -> Union[None, float]:
        """
        Return the computation time [s] for the trajectory.

        :return:
        """
        return self._computation_time

    @computation_time.setter
    def computation_time(self, computation_time):
        if computation_time is not None:
            assert is_real_number(computation_time), "<Solution> computation_time provided as type {}," \
                                                     "but expected type float," \
                                                     "measured in seconds!".format(type(computation_time))
            assert is_positive(computation_time), "<Solution> computation_time needs to be positive!"\
                .format(type(computation_time))
        self._computation_time = computation_time

    def create_dynamic_obstacle(self) -> Dict[int, DynamicObstacle]:
        """
        Creates dynamic obstacle(s) from solution(s) for every planning problem.
        :return:
        """
        obs = {}
        for pp_id, solution in self._planning_problem_solutions.items():
            shape = Rectangle(length=vessel_parameters[solution.vessel_type].l,
                              width=vessel_parameters[solution.vessel_type].w)
            trajectory = Trajectory(initial_time_step=solution.trajectory.initial_time_step + 1,
                                    state_list=solution.trajectory.state_list[1:])
            prediction = TrajectoryPrediction(trajectory, shape=shape)
            obs[pp_id] = DynamicObstacle(obstacle_id=pp_id,
                                         obstacle_type=ObstacleType.MOTORVESSEL,
                                         obstacle_shape=shape,
                                         initial_state=solution.trajectory.state_list[0],
                                         prediction=prediction)

        return obs


class CommonOceanSolutionReader:
    """Reads solution xml files created with the CommonOceanSolutionWriter"""

    @classmethod
    def open(cls, filepath: str) -> Solution:
        """
        Opens and parses the Solution XML file located on the given path.

        :param filepath: Path to the file.
        :return: Solution
        """
        tree = et.parse(filepath)
        root_node = tree.getroot()
        return cls._parse_solution(root_node)

    @classmethod
    def fromstring(cls, file: str) -> Solution:
        """
        Parses the given Solution XML string.

        :param file: xml file as string
        :return: Solution
        """
        root_node = et.fromstring(file)
        return cls._parse_solution(root_node)

    @classmethod
    def _parse_solution(cls, root_node: et.Element) -> Solution:
        """ Parses the Solution XML root node. """  # TODO
        benchmark_id, date, computation_time, processor_name = cls._parse_header(root_node)
        vessels_ids, cost_ids, scenario_id = cls._parse_benchmark_id(benchmark_id)
        pp_solutions = [cls._parse_planning_problem_solution(vessels_ids[idx], cost_ids[idx], trajectory_node)
                        for idx, trajectory_node in enumerate(root_node)]
        return Solution(scenario_id, pp_solutions, date, computation_time, processor_name)

    @staticmethod
    def _parse_header(root_node: et.Element) -> Tuple[str, Union[None, datetime], Union[None, float], Union[None, str]]:
        """ Parses the header attributes for the given Solution XML root node. """
        benchmark_id = root_node.get('benchmark_id')
        if not benchmark_id:
            SolutionException("Solution xml does not have a benchmark id!")

        date = root_node.attrib.get('date', None)  # None if not found
        if date is not None:
            try:
                date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                # backward compatibility with old solution files
                date = datetime.strptime(date, '%Y-%m-%d')

        computation_time = root_node.attrib.get('computation_time', None)
        if computation_time is not None:
            computation_time = float(computation_time)

        processor_name = root_node.attrib.get('processor_name', None)

        return benchmark_id, date, computation_time, processor_name

    @classmethod
    def _parse_planning_problem_solution(cls, vessel_id: str, cost_id: str,
                                         trajectory_node: et.Element) -> PlanningProblemSolution:
        """ Parses PlanningProblemSolution from the given XML node. """
        vessel_model, vessel_type = cls._parse_vessel_id(vessel_id)

        if cost_id not in [cfunc.name for cfunc in CostFunction]:
            raise SolutionReaderException("Invalid Cost ID: " + cost_id)
        cost_function = CostFunction[cost_id]

        pp_id, trajectory = cls._parse_trajectory(trajectory_node)
        return PlanningProblemSolution(pp_id, vessel_model, vessel_type, cost_function, trajectory)

    @classmethod
    def _parse_trajectory(cls, trajectory_node: et.Element) -> Tuple[int, Trajectory]:
        """ Parses Trajectory and planning problem id from the given XML node. """

        if trajectory_node.tag not in [ttype.value for ttype in TrajectoryType]:
            raise SolutionReaderException("Invalid Trajectory Type: " + trajectory_node.tag)
        trajectory_type = TrajectoryType(trajectory_node.tag)

        planning_problem_id = int(trajectory_node.get('planningProblem'))
        state_list = [cls._parse_state(trajectory_type.state_type, state_node) for state_node in trajectory_node]
        state_list = sorted(state_list, key=lambda state: state.time_step)
        return planning_problem_id, Trajectory(initial_time_step=state_list[0].time_step, state_list=state_list)

    @classmethod
    def _parse_sub_element(cls, state_node: et.Element, name: str, as_float: bool = True) -> Union[float, int]:
        """ Parses the sub elements from the given XML node. """
        elem = state_node.find(name)
        if elem is None:
            raise SolutionReaderException("Element '%s' couldn't be found in the xml node!" % name)
        value = float(elem.text) if as_float else int(elem.text)
        return value

    @classmethod
    def _parse_state(cls, state_type: StateType, state_node: et.Element) -> State:
        """ Parses State from the given XML node. """
        if not state_node.tag == state_type.value:
            raise SolutionReaderException("Given xml node is not a '%s' node!" % state_type.value)

        state_vals = {}
        for mapping in list(zip(state_type.xml_fields, state_type.fields)):
            xml_name = mapping[0]
            field_name = mapping[1]
            if isinstance(xml_name, tuple):
                state_vals[field_name] = np.array([cls._parse_sub_element(state_node, name) for name in xml_name])
            else:
                state_vals[field_name] = cls._parse_sub_element(state_node, xml_name, as_float=(not xml_name == 'time'))

        return CustomState(**state_vals)

    @staticmethod
    def _parse_benchmark_id(benchmark_id: str) -> (List[str], List[str], str):
        """ Parses the given benchmark id string. """
        segments = benchmark_id.replace(' ', '').split(':')

        if len(segments) != 4:
            raise SolutionReaderException("Invalid Benchmark ID: " + benchmark_id)

        vessel_model_ids = re.sub(r'[\[\]]', '', segments[0]).split(',')
        cost_function_ids = re.sub(r'[\[\]]', '', segments[1]).split(',')
        scenario_id = ScenarioID.from_benchmark_id(segments[2], segments[3])

        return vessel_model_ids, cost_function_ids, scenario_id

    @staticmethod
    def _parse_vessel_id(vessel_id: str) -> Tuple[VesselModel, VesselType]:
        """ Parses the given vessel id string. """
        if not len(vessel_id) == 3:
            raise SolutionReaderException("Invalid Vessel ID: " + vessel_id)

        if not vessel_id[:2] in [vmodel.name for vmodel in VesselModel]:
            raise SolutionReaderException("Invalid Vessel ID: " + vessel_id)

        if not int(vessel_id[2]) in [vtype.value for vtype in VesselType]:
            raise SolutionReaderException("Invalid Vessel ID: " + vessel_id)

        return VesselModel[vessel_id[:2]], VesselType(int(vessel_id[2]))


class CommonOceanSolutionWriter:

    def __init__(self, solution: Solution):
        """
        Creates the xml file for the given solution that can be dumped as string, or written to file later on.

        :param solution: Solution.
        """
        assert isinstance(solution, Solution)
        self.solution = solution
        self._solution_root = self._serialize_solution(self.solution)

    @staticmethod
    def _get_processor_name() -> Union[str, None]:
        # TODO: compare cpu names with the list of cpu names used on web server

        delete_from_cpu_name = ['(R)', '(TM)']

        def strip_substrings(string: str):
            for del_string in delete_from_cpu_name:
                string = string.replace(del_string, '')
            return string

        if platform.system() == "Windows":
            name_tmp = platform.processor()
            for del_str in delete_from_cpu_name:
                name_tmp.replace(del_str, '')
            return strip_substrings(name_tmp)
        elif platform.system() == "Darwin":
            os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
            command = "sysctl -n machdep.cpu.brand_string"
            return str(subprocess.check_output(command, shell=True).strip())
        elif platform.system() == "Linux":
            command = "cat /proc/cpuinfo"
            all_info = str(subprocess.check_output(command, shell=True).strip())
            for line in all_info.split("\\n"):
                if "model name" in line:
                    name_tmp = re.sub(".*model name.*: ", "", line, 1)
                    return strip_substrings(name_tmp)
        return None

    @classmethod
    def _serialize_solution(cls, solution: Solution) -> et.Element:
        """ Serializes the given solution. """
        root_node = cls._create_root_node(solution)
        for pp_solution in solution.planning_problem_solutions:
            trajectory_node = cls._create_trajectory_node(pp_solution.trajectory_type,
                                                          pp_solution.planning_problem_id,
                                                          pp_solution.trajectory)
            root_node.append(trajectory_node)
        return root_node

    @classmethod
    def _create_root_node(cls, solution: Solution) -> et.Element:
        """ Creates the root node of the Solution XML. """
        root_node = et.Element('CommonOceanSolution')
        root_node.set('benchmark_id', solution.benchmark_id)
        if solution.computation_time is not None:
            root_node.set('computation_time', str(solution.computation_time))
        if solution.date is not None:
            root_node.set('date', solution.date.strftime('%Y-%m-%dT%H:%M:%S'))
        processor_name = cls._get_processor_name() if solution.processor_name == 'auto' else solution.processor_name
        if processor_name is not None:
            root_node.set('processor_name', processor_name)
        return root_node

    @classmethod
    def _create_trajectory_node(cls, trajectory_type: TrajectoryType, pp_id: int, trajectory: Trajectory) -> et.Element:
        """ Creates the Trajectory XML Node for the given trajectory. """
        trajectory_node = et.Element(trajectory_type.value)
        trajectory_node.set('planningProblem', str(pp_id))
        for state in trajectory.state_list:
            state_node = cls._create_state_node(trajectory_type.state_type, state)
            trajectory_node.append(state_node)
        return trajectory_node

    @classmethod
    def _create_sub_element(cls, name: str, value: Union[float, int]) -> et.Element:
        """ Creates an XML element for the given value. """
        element = et.Element(name)
        element.text = str(np.float64(value) if isinstance(value, float) else value)
        return element

    @classmethod
    def _create_state_node(cls, state_type: StateType, state: State) -> et.Element:
        """ Creates XML nodes for the States of the Trajectory. """
        state_node = et.Element(state_type.value)
        for mapping in list(zip(state_type.xml_fields, state_type.fields)):
            xml_name = mapping[0]
            state_val = getattr(state, mapping[1])
            if isinstance(xml_name, tuple):
                for idx, name in enumerate(xml_name):
                    state_node.append(cls._create_sub_element(name, state_val[idx]))
            else:
                state_node.append(cls._create_sub_element(xml_name, state_val))
        return state_node

    def dump(self, pretty: bool = True) -> str:
        """
        Dumps the Solution XML as string.

        :param pretty: If set to true, prettifies the xml string.
        :return: string - Solution XML as string.
        """
        rough_string = et.tostring(self._solution_root, encoding='utf-8')

        if not pretty:
            return rough_string

        parsed = minidom.parseString(rough_string)
        return parsed.toprettyxml(indent="  ")

    def write_to_file(self, output_path: str = './', filename: str = None,
                      overwrite: bool = False, pretty: bool = True):
        """
        Writes the Solution XML to a file.

        :param output_path: Output dir where the Solution XML file should be written to. \
            Writes to the same folder where it is called from if not specified.
        :param filename: Name of the Solution XML file. If not specified, sets the name as 'solution_BENCHMARKID.xml' \
            where the BENCHMARKID is the benchmark_id of the solution.
        :param overwrite: If set to True, overwrites the file if it already exists.
        :param pretty: If set to True, prettifies the Solution XML string before writing to file.
        """
        filename = filename if filename is not None else 'solution_%s.xml' % self.solution.benchmark_id
        fullpath = os.path.join(output_path, filename) if filename is not None else os.path.join(output_path, filename)

        if not os.path.exists(os.path.dirname(fullpath)):
            raise NotADirectoryError("Directory %s does not exist." % os.path.dirname(fullpath))

        if os.path.exists(fullpath) and not overwrite:
            raise FileExistsError("File %s already exists. If you want to overwrite it set overwrite=True." % fullpath)

        with open(fullpath, 'w') as f:
            f.write(self.dump(pretty))
