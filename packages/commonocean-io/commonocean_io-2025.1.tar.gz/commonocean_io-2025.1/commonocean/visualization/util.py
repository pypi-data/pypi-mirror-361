import warnings
import numpy as np
from commonroad.scenario.scenario import Scenario
from matplotlib.lines import Line2D
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.collections as collections
from typing import List, Dict, Tuple, Union
from commonroad.geometry.shape import Rectangle
from commonroad.geometry.transform import rotate_translate

from commonocean.scenario.obstacle import DynamicObstacle
from commonocean.scenario.waters import WatersNetwork

# Tunneling from CR-IO #
from commonroad.visualization.util import draw_polygon_as_patch as draw_polygon_as_patch_cr
from commonroad.visualization.util import draw_polygon_collection_as_patch as draw_polygon_collection_as_patch_cr
########################

__author__ = "Hanna Krasowski, Benedikt Pfleiderer, Fabian Thomas-Barein"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"


class LineDataUnits(Line2D):
    def __init__(self, *args, **kwargs):
        _lw_data = kwargs.pop("linewidth", 1)
        super().__init__(*args, **kwargs)
        self._lw_data = _lw_data

    def _get_lw(self):
        if self.axes is not None:
            ppd = 72. / self.axes.figure.dpi
            trans = self.axes.transData.transform
            return ((trans((1, self._lw_data)) - trans((0, 0))) * ppd)[1]
        else:
            return 1

    def _set_lw(self, lw):
        self._lw_data = lw

    _linewidth = property(_get_lw, _set_lw)

def get_vehicle_direction_triangle(rect: Rectangle) -> np.ndarray:
    """
    :returns vertices of triangle pointing in the driving direction
    """
    l = rect.length * 0.49
    w = rect.width * 0.49
    dist = min(l+1.0, 0.65*rect.width)
    vertices = np.array([[l - dist,  w],
                         [l - dist, -w],
                         [l, 0.0]])
    return rotate_translate(vertices, rect.center, rect.orientation)

def get_tangent_angle(points, rel_angle=0.0):
    vec = points[1:] - points[0:-1]
    angle = np.arctan2(vec[:, 1], vec[:, 0])
    angle -= rel_angle
    angle = np.where(angle >= 0.0, angle, angle + 2 * np.pi) * 180.0 / np.pi
    return angle


def draw_polygon_as_patch(vertices, ax, zorder=5, facecolor='#ffffff',
                          edgecolor='#000000', lw=0.5, alpha=1.0) -> mpl.patches.Patch:
    """
    vertices are no closed polygon (first element != last element)
    """
    
    return draw_polygon_as_patch_cr(vertices, ax, zorder, facecolor, edgecolor, lw, alpha)


def draw_polygon_collection_as_patch(vertices: List[list], ax, zorder=5, facecolor='#ffffff',
                                     edgecolor='#000000', lw=0.5, alpha=1.0,
                                     antialiased=True) -> mpl.collections.Collection:
    """
    vertices are no closed polygon (first element != last element)
    """
    
    return draw_polygon_collection_as_patch_cr(vertices, ax, zorder, facecolor, edgecolor, lw, alpha, antialiased)


def approximate_bounding_box_dyn_obstacles(obj: list, time_step=0) -> Union[Tuple[list], None]:
    """
    Compute bounding box of dynamic obstacles at time step
    :param obj: All possible objects. DynamicObstacles are filtered.
    :return:
    """

    def update_bounds(new_point: np.ndarray, bounds: List[list]):
        """Update bounds with new point"""
        if new_point[0] < bounds[0][0]:
            bounds[0][0] = new_point[0]
        if new_point[1] < bounds[1][0]:
            bounds[1][0] = new_point[1]
        if new_point[0] > bounds[0][1]:
            bounds[0][1] = new_point[0]
        if new_point[1] > bounds[1][1]:
            bounds[1][1] = new_point[1]

        return bounds

    dynamic_obstacles_filtered = []
    for o in obj:
        if type(o) == DynamicObstacle:
            dynamic_obstacles_filtered.append(o)
        elif type(o) == Scenario:
            dynamic_obstacles_filtered.extend(o.dynamic_obstacles)

    x_int = [np.inf, -np.inf]
    y_int = [np.inf, -np.inf]
    bounds = [x_int, y_int]

    for obs in dynamic_obstacles_filtered:
        occ = obs.occupancy_at_time(time_step)
        if occ is None: continue
        shape = occ.shape
        if hasattr(shape, 'center'):
            bounds = update_bounds(shape.center, bounds=bounds)
        elif hasattr(shape, 'vertices'):
            v = shape.vertices
            bounds = update_bounds(np.min(v, axis=0), bounds=bounds)
            bounds = update_bounds(np.max(v, axis=0), bounds=bounds)

    if np.inf in bounds[0] or -np.inf in bounds[0] or np.inf in bounds[1] or -np.inf in bounds[1]:
        return None
    else:
        return tuple(bounds)

def colormap_idx(max_x):
    norm = mpl.colors.Normalize(vmin=0, vmax=max_x)
    colormap = cm.ScalarMappable(norm=norm, cmap=cm.jet)
    # Closure
    return lambda x: colormap.to_rgba(x)