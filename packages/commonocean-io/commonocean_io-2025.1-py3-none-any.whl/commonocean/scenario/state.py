__author__ = "Bruno Maione"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2023a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "development"

from commonroad.common.util import Interval, AngleInterval
from commonroad.geometry.shape import Shape
from commonroad.scenario.state import State
from dataclasses import dataclass
from typing import Any, Union
import numpy as np
import math

FloatExactOrInterval = Union[float, Interval]
AngleExactOrInterval = Union[float, AngleInterval]
ExactOrShape = Union[np.ndarray, Shape]

@dataclass(eq=False)
class PMState(State):
    """
    This is a class representing Point Mass State (PM State).

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param velocity: Velocity :math:`v_x` in longitudinal direction
    :param velocity_y: Velocity :math:`v_x` in lateral direction
    """
    position: ExactOrShape = None
    velocity: FloatExactOrInterval = None
    velocity_y: FloatExactOrInterval = None

    def make_orientation_valid(self):
        return self

@dataclass(eq=False)
class YPState(State):
    """
    This is a class representing Yaw-Constrained State (YP State).

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param orientation: Yaw angle :math:`\\Psi`
    :param velocity: Velocity :math:`n` aligned with the orientation of the vessel (also called surge)
    """
    position: ExactOrShape = None
    orientation: AngleExactOrInterval = None
    velocity: FloatExactOrInterval = None

    def make_orientation_valid(self):
        self.orientation = self.orientation % (2 * math.pi)
        return self

@dataclass(eq=False)
class TFState(State):
    """
    This is a class representing Three Degrees of Freedom Model (3F State).

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param orientation: Yaw angle :math:`\\Psi`
    :param velocity: Velocity :math:`n` aligned with the orientation of the vessel (also called surge)
    :param velocity_y: Velocity :math:`v` lateral to the orientation of the vessel (also called sway)
    :param yaw_rate: Yaw rate :math:`\\omega`
    """
    position: ExactOrShape = None
    orientation: AngleExactOrInterval = None
    velocity: FloatExactOrInterval = None
    velocity_y: FloatExactOrInterval = None
    yaw_rate: FloatExactOrInterval = None

    def make_orientation_valid(self):
        self.orientation = self.orientation % (2 * math.pi)
        return self

@dataclass(eq=False)
class PMStateSIM(State):
    """
    This is a class representing .

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param orientation: Yaw angle :math:`\\Psi`
    :param velocity: Velocity :math:`n` aligned with the orientation of the vessel (also called surge)
    """
    position: ExactOrShape = None
    velocity: FloatExactOrInterval = None
    velocity_y: FloatExactOrInterval = None
    acceleration: FloatExactOrInterval = None
    acceleration_y: FloatExactOrInterval = None


@dataclass(eq=False)
class YPStateSIM(State):
    """
    This is a class representing .

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param orientation: Yaw angle :math:`\\Psi`
    :param velocity: Velocity :math:`n` aligned with the orientation of the vessel (also called surge)
    """
    position: ExactOrShape = None
    orientation: AngleExactOrInterval = None
    velocity: FloatExactOrInterval = None
    acceleration: FloatExactOrInterval = None
    yaw_rate: FloatExactOrInterval = None

    def make_orientation_valid(self):
        self.orientation = self.orientation % (2 * math.pi)
        return self

SpecificStateClasses = [PMState, YPState, TFState, PMStateSIM, YPStateSIM]



@dataclass(eq=False)
class PMInputState(State):
    """
    This is a class representing the input for PM model (PM Input).

    :param acceleration: Acceleration :math:`a_x`
    :param acceleration_y: Acceleration :math:`a_y`
    """

    acceleration: FloatExactOrInterval = None
    acceleration_y: FloatExactOrInterval = None

@dataclass(eq=False)
class YPInputState(State):
    """
    This is a class representing the input for YP model (YP Input).

    :param acceleration: acceleration aligned with orientation
    :param yaw_rate: yaw aligned with orientation
    """

    acceleration: FloatExactOrInterval = None
    yaw_rate: FloatExactOrInterval = None

@dataclass(eq=False)
class TFInputState(State):
    """
    This is a class representing the input for TF model (TF Input).

    :param force_orientation: body-fixed force aligned with orientation
    :param force_lateral: body-fixed force lateral to orientation
    :param yaw_moment: body-fixed yaw moment
    """

    force_orientation: FloatExactOrInterval = None
    force_lateral: FloatExactOrInterval = None
    yaw_moment: FloatExactOrInterval = None



@dataclass(eq=False)
class InitialState(State):
    """
    This is a class representing Initial State (general, for all three models).

    :param position: Position :math:`s_x`- and :math:`s_y` in a global coordinate system
    :param velocity: Velocity :math:`v_x` in longitudinal direction
    :param velocity_y: Velocity :math:`v_x` in lateral direction
    :param orientation: Yaw angle :math:`\\Psi`
    :param yaw_rate: Yaw rate :math:`\\omega`
    """

    position: ExactOrShape = None
    velocity: FloatExactOrInterval = None
    velocity_y: FloatExactOrInterval = None
    orientation: AngleExactOrInterval = None
    yaw_rate: FloatExactOrInterval = None
