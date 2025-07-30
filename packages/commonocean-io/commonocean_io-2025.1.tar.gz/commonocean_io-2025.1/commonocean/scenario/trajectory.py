__author__ = "Bruno Maione"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2023a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "development"

from commonroad.scenario.trajectory import Trajectory as Trajectory_CR
from commonroad.scenario.state import State
from typing import List

class Trajectory(Trajectory_CR):
    """ Class to model the movement of an object over time. The states of the
    trajectory can be either exact or uncertain; however,
    only exact time_step are allowed. """

    def __init__(self, initial_time_step: int, state_list: List[State]):
        """
        :param initial_time_step: initial time step of the trajectory
        :param state_list: ordered sequence of states over time representing
        the trajectory. It is assumed that
        the time discretization between two states matches the time
        discretization of the scenario.
        """
        super().__init__(initial_time_step, state_list)