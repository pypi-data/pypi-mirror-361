from abc import ABC, abstractmethod
from typing import Union, Tuple, Optional

from commonocean.visualization.param_server import ParamServer
from commonocean.visualization.renderer import IRenderer

__author__ = "Hanna Krasowski"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"



class IDrawable(ABC):
    """
    Interface for drawable types
    """

    @abstractmethod
    def draw(self, renderer: IRenderer, draw_params: Union[ParamServer, dict, None]) -> None:
        """
        Draw the object

        :param renderer: Renderer to use for drawing
        :param draw_params: Optional parameters ovrriding the defaults for plotting given by a nested dict that
            recreates the structure of an object or a ParamServer object
        :param call_stack: Optional tuple of string containing the call stack, which allows for differentiation of
            plotting styles depending on the call stack
        :return: None
        """
        pass
