import os
from collections import defaultdict
from typing import Dict, Set
from copy import deepcopy

import matplotlib as mpl
import matplotlib.artist as artists
import matplotlib.collections as collections
import matplotlib.colors
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.text as text
from matplotlib.animation import FuncAnimation
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv, to_rgb, to_hex
from matplotlib.path import Path

import commonroad.geometry.shape
import commonroad.prediction.prediction

import commonocean.scenario.obstacle
from commonroad.common.util import Interval
from commonroad.geometry.shape import *
from commonocean.planning.goal import GoalRegion
from commonocean.planning.planning_problem import PlanningProblemSet, PlanningProblem
from commonocean.prediction.prediction import Occupancy, TrajectoryPrediction
from commonroad.scenario.obstacle import PhantomObstacle, EnvironmentObstacle
from commonocean.scenario.obstacle import DynamicObstacle, StaticObstacle, Obstacle, ObstacleRole, ObstacleType
from commonocean.scenario.scenario import Scenario
from commonocean.scenario.trajectory import Trajectory
from commonroad.scenario.state import State
from commonroad.visualization.icons import supported_icons, get_obstacle_icon_patch  # TODO: recraft these for co
from commonocean.visualization.param_server import (
    ParamServer,
    DynamicObstacleParams,
    InitialStateParams,
    MPDrawParams,
    OccupancyParams,
    OptionalSpecificOrAllDrawParams,
    PlanningProblemParams,
    PlanningProblemSetParams,
    ShapeParams,
    StateParams,
    StaticObstacleParams,
    TrajectoryParams,
)
from commonocean.visualization.renderer import IRenderer
from commonocean.visualization.util import get_vehicle_direction_triangle, get_tangent_angle, \
    approximate_bounding_box_dyn_obstacles
from commonocean.visualization.util import colormap_idx

from commonocean.scenario.waters import WatersNetwork

__author__ = "Hanna Krasowski, Stefan Schaerdinger"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "development"

traffic_sign_path = os.path.join(os.path.dirname(__file__), 'traffic_signs/')


class ZOrders:
    # Map
    LANELET_POLY = 9.0
    INCOMING_POLY = 9.1
    CROSSING_POLY = 9.2
    CENTER_BOUND = 10.0
    LIGHT_STATE_OTHER = 10.0
    LIGHT_STATE_GREEN = 10.05
    DIRECTION_ARROW = 10.1
    SUCCESSORS = 11.0
    STOP_LINE = 11.0
    RIGHT_BOUND = 12.0
    LEFT_BOUND = 12.0
    # Obstacles
    OBSTACLES = 20.0
    CAR_PATCH = 20.0
    # Labels
    LANELET_LABEL = 30.2
    STATE = 100.0
    LABELS = 1000.0
    # Values added to base value from drawing parameters
    INDICATOR_ADD = 0.2
    BRAKING_ADD = 0.2
    HORN_ADD = 0.1
    BLUELIGHT_ADD = 0.1


class MPRenderer(IRenderer):

    def __init__(self, draw_params: Union[MPDrawParams, None] = None,
                 plot_limits: Union[List[Union[int, float]], None] = None, ax: Union[mpl.axes.Axes, None] = None,
                 figsize: Union[None, Tuple[float, float]] = None, focus_obstacle: Union[None, Obstacle] = None):
        """
        Creates an renderer for matplotlib

        :param draw_params: Default drawing params, if not supplied, default values are used.
        :param plot_limits: plotting limits. If not supplied, using `ax.autoscale()`.
        :param ax: Axis to use. If not supplied, `pyplot.gca()` is used.
        :param figsize: size of the figure
        :param focus_obstacle: if provided, the plot_limits are centered around center of obstacle at time_begin
        """

        self._plot_limits = None
        if draw_params is None:
            self.draw_params = MPDrawParams()
        else:
            self.draw_params = draw_params

        if ax is None:
            self.ax = plt.gca()
        else:
            self.ax = ax

        self.f = self.ax.figure

        if figsize is not None:
            self.f.set_size_inches(*figsize)

        # Draw elements
        self.dynamic_artists = []
        self.dynamic_collections = []
        self.static_artists = []
        self.static_collections = []
        self.obstacle_patches = []
        self.traffic_sign_artists = []
        self.traffic_signs = []
        self.traffic_sign_call_stack = tuple()
        self.traffic_sign_draw_params = self.draw_params
        # labels of dynamic elements
        self.dynamic_labels = []

        # current center of focus obstacle
        self.plot_center = None
        self.callbacks = defaultdict(list)
        self.focus_obstacle_id = focus_obstacle.obstacle_id if focus_obstacle is not None else None
        self.plot_limits = plot_limits

    @property
    def plot_limits(self):
        if self.focus_obstacle_id is not None and self._plot_limits is None:
            # Make sure plot limits are not None if focus obstacle is activated. Otherwise, focus obstacle doesn't work.
            return [-20.0, 20.0, -20.0, 20.0]
        else:
            return self._plot_limits

    @plot_limits.setter
    def plot_limits(self, val: List[Union[float, int, List[Union[float, int]]]]):
        if val is not None and isinstance(val[0], List):
            self._plot_limits = val[0] + val[1]
        elif isinstance(val, List) or val == "auto":
            self._plot_limits = val
        elif val is not None:
            raise ValueError(f"Invalid plot_limit: {val}")

    @property
    def plot_limits_focused(self):
        """
        :returns: plot limits centered around focus_obstacle_id defined in draw_params
        """
        if self._plot_limits is not None and (self._plot_limits == "auto" or self.plot_center is None):
            return self._plot_limits
        elif self.plot_center is not None:
            plot_limits_f = np.array(self.plot_limits, dtype=int)
            plot_limits_f[:2] += int(self.plot_center[0])
            plot_limits_f[2:] += int(self.plot_center[1])
            return plot_limits_f

    def add_callback(self, event, func):
        self.callbacks[event].append(func)

    def draw_list(self, drawable_list: List[IDrawable],
                  draw_params: Union[MPDrawParams, List[Optional[ParamServer]], None] = None) -> None:
        """
        Simple wrapper to draw a list of drawable objects

        :param drawable_list: Objects to draw
        :param draw_params: optional parameters for plotting, overriding the parameters of the renderer
        :return: None
        """
        if not isinstance(draw_params, list):
            draw_params = [draw_params] * len(drawable_list)
        assert len(draw_params) == len(
            drawable_list), f"Number of drawables has to match number of draw params {len(drawable_list)} vs. " \
                            f"{len(draw_params)}!"
        for elem, params in zip(drawable_list, draw_params):
            elem.draw(self, params)

    def _get_draw_params(self, draw_params: Union[MPDrawParams, None]) -> MPDrawParams:
        if draw_params is None:
            draw_params = self.draw_params
        return draw_params

    def clear(self, keep_static_artists=False) -> None:
        """
        Clears the internal drawing buffer

        :return: None
        """
        self.plot_center = None
        self.obstacle_patches.clear()
        self.traffic_signs.clear()
        self.traffic_sign_call_stack = tuple()
        self.traffic_sign_draw_params = self.draw_params
        self.dynamic_artists.clear()
        self.dynamic_collections.clear()
        self.traffic_sign_artists.clear()
        self.dynamic_labels.clear()
        if keep_static_artists is False:
            self.static_artists.clear()
            self.static_collections.clear()

    def remove_dynamic(self) -> None:
        """
        Remove the dynamic objects from their current axis

        :return: None
        """
        for art in self.dynamic_artists:
            art.remove()

        # text artists cannot be removed -> set invisble
        for t in self.dynamic_labels:
            t.set_visible(False)
        self.dynamic_labels.clear()

    def render_dynamic(self) -> List[artists.Artist]:
        """
        Only render dynamic objects from buffer

        :return: List of drawn object's artists
        """
        artist_list = []
        # self.traffic_sign_artists = draw_traffic_light_signs(self.traffic_signs, self.traffic_sign_draw_params,
        #                                                     self.traffic_sign_call_stack, self)
        for art in self.dynamic_artists:
            self.ax.add_artist(art)
            artist_list.append(art)
        # for art in self.traffic_sign_artists:
        #    self.ax.add_artist(art)
        #    artist_list.append(art)
        for col in self.dynamic_collections:
            self.ax.add_collection(col)
            artist_list.append(col)
        for t in self.dynamic_labels:
            self.ax.add_artist(t)

        self.obstacle_patches.sort(key=lambda x: x.zorder)
        patch_col = mpl.collections.PatchCollection(self.obstacle_patches, match_original=True,
                                                    zorder=ZOrders.OBSTACLES)
        self.ax.add_collection(patch_col)
        artist_list.append(patch_col)
        self.dynamic_artists = artist_list
        self._connect_callbacks()

        return artist_list

    def render_static(self) -> List[artists.Artist]:
        """
        Only render static objects from buffer

        :return: List of drawn object's artists
        """
        for col in self.static_collections:
            self.ax.add_collection(col)
        for art in self.static_artists:
            self.ax.add_artist(art)

        self._connect_callbacks()
        return self.static_collections + self.static_artists

    def render(self, show: bool = False, filename: str = None, keep_static_artists=False) -> List[artists.Artist]:
        """
        Render all objects from buffer

        :param show: Show the resulting figure
        :param filename: If provided, saves the figure to the provided file
        :return: List of drawn object's artists
        """
        self.ax.cla()
        artists_list = self.render_static()
        artists_list.extend(self.render_dynamic())

        if self.plot_limits is None:
            self.ax.autoscale(True)
        else:
            self.ax.set_xlim(self.plot_limits_focused[:2])
            self.ax.set_ylim(self.plot_limits_focused[2:])
        self.ax.set_aspect('equal')
        if filename is not None:
            self.f.savefig(filename, bbox_inches='tight')
        if show:
            self.f.show()

        # if self.draw_params.by_callstack(param_path="axis_visible", call_stack=()) is False:
        #     self.ax.axes.xaxis.set_visible(False)
        #     self.ax.axes.yaxis.set_visible(False)

        self.clear(keep_static_artists)
        return artists_list

    def _connect_callbacks(self):
        """
        Connects collected callbacks with ax object.
        :return:
        """
        for event, funcs in self.callbacks.items():
            for fun in funcs:
                self.ax.callbacks.connect(event, fun)

        self.ax_updated = False

    def create_video(self, obj_lists: List[IDrawable], file_path: str, delta_time_steps: int = 1, plotting_horizon=0,
                     draw_params: Union[List[Optional[ParamServer]], ParamServer, None] = None, fig_size: Union[list, None] = None,
                     dt=100, dpi=120) -> None:
        """
        Creates a video of one or multiple CommonRoad objects in mp4, gif,
        or avi format.

        :param obj_lists: list of objects to be plotted.
        :param file_path: filename of generated video (ends on .mp4/.gif/.avi, default mp4, when nothing is specified)
        :param delta_time_steps: plot every delta_time_steps time steps of scenario
        :param plotting_horizon: time steps of prediction plotted in each frame
        :param draw_params: parameters for plotting given by a nested dict
            that recreates the structure of an object or a MPDrawParams object
        :param fig_size: size of the video
        :param dt: time step between frames in ms
        :param dpi: resolution of the video
        :return: None
        """
        if not isinstance(draw_params, list):
            draw_params = [draw_params] * len(obj_lists)
        for i, p in enumerate(draw_params):
            draw_params[i] = self._get_draw_params(p)
        time_begin = draw_params[0]['time_begin']
        time_end = draw_params[0]['time_end']
        assert time_begin < time_end, '<video/create_scenario_video> ' \
                                      'time_begin=%i needs to smaller than ' \
                                      'time_end=%i.' % (time_begin, time_end)

        if fig_size is None:
            fig_size = [15, 8]

        self.ax.clear()
        self.f.set_size_inches(*fig_size)
        self.ax.set_aspect('equal')

        def init_frame():
            [p.update({'time_begin': time_begin, 'time_end': time_begin + delta_time_steps}) for p in draw_params]
            self.draw_list(obj_lists, draw_params=draw_params)
            self.render_static()
            artists = self.render_dynamic()
            if self.plot_limits is None:
                self.ax.autoscale()
            elif self.plot_limits == 'auto':
                limits = approximate_bounding_box_dyn_obstacles(obj_lists, time_begin)
                if limits is not None:
                    self.ax.xlim(limits[0][0] - 10, limits[0][1] + 10)
                    self.ax.ylim(limits[1][0] - 10, limits[1][1] + 10)
                else:
                    self.ax.autoscale()
            else:
                self.ax.set_xlim(self.plot_limits_focused[0], self.plot_limits_focused[1])
                self.ax.set_ylim(self.plot_limits_focused[2], self.plot_limits_focused[3])

            if draw_params[0].by_callstack(param_path="axis_visible", call_stack=()) is False:
                self.ax.axes.xaxis.set_visible(False)
                self.ax.axes.yaxis.set_visible(False)
            return artists

        def update(frame=0):
            [p.update({'time_begin': time_begin + delta_time_steps * frame,
                       'time_end': time_begin + min(frame_count, delta_time_steps * frame + plotting_horizon)}) for p in
             draw_params]
            self.remove_dynamic()
            self.clear()
            self.draw_list(obj_lists, draw_params=draw_params)
            artists = self.render_dynamic()
            if self.plot_limits is None:
                self.ax.autoscale()
            elif self.plot_limits == 'auto':
                limits = approximate_bounding_box_dyn_obstacles(obj_lists, time_begin)
                if limits is not None:
                    self.ax.xlim(limits[0][0] - 10, limits[0][1] + 10)
                    self.ax.ylim(limits[1][0] - 10, limits[1][1] + 10)
                else:
                    self.ax.autoscale()
            else:
                self.ax.set_xlim(self.plot_limits_focused[0], self.plot_limits_focused[1])
                self.ax.set_ylim(self.plot_limits_focused[2], self.plot_limits_focused[3])
            return artists

        # Min frame rate is 1 fps
        dt = min(1000.0, dt)
        frame_count = (time_end - time_begin) // delta_time_steps
        plt.ioff()
        # Interval determines the duration of each frame in ms
        anim = FuncAnimation(self.f, update, frames=frame_count, init_func=init_frame, blit=False, interval=dt)

        if not any([file_path.endswith('.mp4'), file_path.endswith('.gif'), file_path.endswith('.avi')]):
            file_path += '.mp4'
        fps = int(math.ceil(1000.0 / dt))
        interval_seconds = dt / 1000.0
        anim.save(file_path, dpi=dpi, writer='ffmpeg', fps=fps,
                  extra_args=["-g", "1", "-keyint_min", str(interval_seconds)])
        self.clear()
        self.ax.clear()

    def add_legend(self, legend: Dict[Tuple[str, ...], str],
                   draw_params: Union[MPDrawParams, None] = None) -> None:
        """
        Adds legend with color of objects specified by legend.keys() and
        texts specified by legend.values().

        :param legend: color of objects specified by path in legend.keys() and texts specified by legend.values()
        :param draw_params: draw parameters used for plotting (color is extracted using path in legend.keys())
        :return: None
        """
        draw_params = self._get_draw_params(draw_params)
        handles = []
        for obj_name, text in legend.items():
            try:
                color = draw_params[obj_name]
            except KeyError:
                color = None
            if color is not None:
                handles.append(mpl.patches.Patch(color=color, label=text))

        legend = self.ax.legend(handles=handles)
        legend.set_zorder(ZOrders.LABELS)

    def draw_scenario(self, obj: Scenario, draw_params: Union[MPDrawParams, None]) -> None:
        """
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
            that recreates the structure of an object or a MPDrawParams object
        :return: None
        """
        draw_params = self._get_draw_params(draw_params)

        # TODO: add waters network func
        # obj._waters_network.draw(self, draw_params, call_stack)
        # obj.lanelet_network.draw(self, draw_params, call_stack)
        # PREV: obj.lanelet_network.draw(self, draw_params, call_stack)

        obs = obj.obstacles
        # Draw all objects
        for o in obs:
            if isinstance(o, DynamicObstacle):
                o.draw(self, draw_params.dynamic_obstacle)
            elif isinstance(o, StaticObstacle):
                o.draw(self, draw_params.static_obstacle)
            elif isinstance(o, EnvironmentObstacle):
                o.draw(self, draw_params.environment_obstacle)
            else:
                o.draw(self, draw_params.phantom_obstacle)

    def draw_static_obstacle(self, obj: StaticObstacle,
                             draw_params: OptionalSpecificOrAllDrawParams[StaticObstacleParams] = None) -> None:
        """
        :param obj: object to be plotted
        :param draw_params: optional parameters for plotting, overriding the parameters of the renderer
        :return: None
        """
        if draw_params is None:
            draw_params = self.draw_params.static_obstacle
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.static_obstacle

        time_begin = draw_params.time_begin
        occ = obj.occupancy_at_time(time_begin)
        self._draw_occupancy(occ, obj.initial_state, draw_params.occupancy)

    def _draw_occupancy(self, occ: Occupancy, state: State,
                        draw_params: OptionalSpecificOrAllDrawParams[OccupancyParams] = None) -> None:
        if draw_params is None:
            draw_params = self.draw_params.occupancy
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.occupancy
        if occ is not None:
            occ.draw(self, draw_params)
        if state is not None and state.is_uncertain_position:
            shape_params = deepcopy(draw_params.uncertain_position)
            shape_params.zorder = 0.1 + draw_params.shape.zorder
            state.position.draw(self, shape_params)

    def draw_dynamic_obstacle(self, obj: DynamicObstacle,
                              draw_params: OptionalSpecificOrAllDrawParams[DynamicObstacleParams]) -> None:
        """
        :param obj: object to be plotted
        :param draw_params: optional parameters for plotting, overriding the parameters of the renderer
        :return: None
        """
        if draw_params is None:
            draw_params = self.draw_params.dynamic_obstacle
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.dynamic_obstacle

        time_begin = draw_params.time_begin
        time_end = draw_params.time_end
        focus_obstacle_id = self.focus_obstacle_id
        draw_icon = draw_params.draw_icon
        show_label = draw_params.show_label
        draw_shape = draw_params.draw_shape
        draw_direction = draw_params.draw_direction
        draw_initial_state = draw_params.draw_initial_state
        draw_occupancies = draw_params.occupancy.draw_occupancies
        draw_signals = draw_params.draw_signals
        draw_trajectory = draw_params.trajectory.draw_trajectory

        draw_history = draw_params.history.draw_history

        if obj.prediction is None and obj.initial_state.time_step < time_begin or obj.initial_state.time_step > \
                time_end:
            return
        elif (
                obj.prediction is not None and obj.prediction.final_time_step < time_begin) or \
                obj.initial_state.time_step > time_end:
            return

        if draw_history and isinstance(obj.prediction, commonroad.prediction.prediction.TrajectoryPrediction):
            self._draw_history(obj, draw_params)

        # draw car icon
        if draw_icon and obj.obstacle_type in supported_icons() and type(
                obj.prediction) == commonroad.prediction.prediction.TrajectoryPrediction:

            try:
                length = obj.obstacle_shape.length
                width = obj.obstacle_shape.width
            except AttributeError:
                draw_shape = True
                draw_icon = False

            if draw_icon:
                draw_shape = False
                if time_begin == obj.initial_state.time_step:
                    inital_state = obj.initial_state
                else:
                    inital_state = obj.prediction.trajectory.state_at_time_step(time_begin)
                if inital_state is not None:
                    vehicle_color = draw_params.vehicle_shape.occupancy.shape.facecolor
                    vehicle_edge_color = draw_params.vehicle_shape.occupancy.shape.edgecolor
                    self.obstacle_patches.extend(get_obstacle_icon_patch(obj.obstacle_type, inital_state.position[0],
                                                                         inital_state.position[1],
                                                                         inital_state.orientation,
                                                                         vehicle_length=length, vehicle_width=width,
                                                                         vehicle_color=vehicle_color,
                                                                         edgecolor=vehicle_edge_color,
                                                                         zorder=ZOrders.CAR_PATCH))
        elif draw_icon is True:
            draw_shape = True

        # draw shape
        if draw_shape:
            veh_occ = obj.occupancy_at_time(time_begin)
            if veh_occ is not None:
                self._draw_occupancy(veh_occ, obj.initial_state, draw_params.vessel_shape.occupancy)
                if draw_direction and veh_occ is not None and type(veh_occ.shape) == Rectangle:
                    v_tri = get_vehicle_direction_triangle(veh_occ.shape)
                    self.draw_polygon(v_tri, draw_params.vehicle_shape.direction)


        # draw occupancies
        if draw_occupancies and type(obj.prediction) == commonroad.prediction.prediction.SetBasedPrediction:
            if draw_shape:
                # occupancy already plotted
                time_begin_occ = time_begin + 1
            else:
                time_begin_occ = time_begin

            for time_step in range(time_begin_occ, time_end):
                state = None
                if isinstance(obj.prediction, TrajectoryPrediction):
                    state = obj.prediction.trajectory.state_at_time_step(time_step)
                occ = obj.occupancy_at_time(time_step)
                self._draw_occupancy(occ, state, draw_params.occupancy)

        # draw trajectory
        if draw_trajectory and type(obj.prediction) == commonroad.prediction.prediction.TrajectoryPrediction:
            obj.prediction.trajectory.draw(self, draw_params.trajectory)

        # get state
        state = None
        if time_begin == 0:
            state = obj.initial_state
        elif type(obj.prediction) == commonroad.prediction.prediction.TrajectoryPrediction:
            state = obj.prediction.trajectory.state_at_time_step(time_begin)

        # set plot center state
        if focus_obstacle_id == obj.obstacle_id and state is not None:
            self.plot_center = state.position

        # draw label
        if show_label:
            if state is not None:
                position = state.position
                self.dynamic_labels.append(text.Text(position[0] + 0.5, position[1], str(obj.obstacle_id), clip_on=True,
                                                     zorder=ZOrders.LABELS))

        # draw initial state
        if draw_initial_state and state is not None:
            state.draw(self, draw_params.state)

    def _draw_history(self, dyn_obs: DynamicObstacle, draw_params: DynamicObstacleParams):
        """
        Draws history occupancies of the dynamic obstacle

        which allows for differentiation of plotting styles
               depending on the call stack of drawing functions
        :param draw_params: parameters for plotting, overriding the parameters of the renderer
        :param dyn_obs: the dynamic obstacle
        :return:
        """
        time_begin = draw_params.time_begin
        history_base_color = draw_params.vehicle_shape.occupancy.shape.facecolor
        history_steps = draw_params.history.steps
        history_fade_factor = draw_params.history.fade_color
        history_step_size = draw_params.history.step_size
        history_base_color = rgb_to_hsv(to_rgb(history_base_color))
        occupancy_params = deepcopy(draw_params.vehicle_shape.occupancy)
        for history_idx in range(history_steps, 0, -1):
            time_step = time_begin - history_idx * history_step_size
            occ = dyn_obs.occupancy_at_time(time_step)
            if occ is not None:
                color_hsv_new = history_base_color.copy()
                color_hsv_new[2] = max(0, color_hsv_new[2] - history_fade_factor * history_idx)
                color_hex_new = to_hex(hsv_to_rgb(color_hsv_new))
                occupancy_params.facecolor = color_hex_new
                occ.draw(self, occupancy_params)

    def draw_trajectory(self, obj: Trajectory,
                        draw_params: OptionalSpecificOrAllDrawParams[TrajectoryParams] = None) -> None:
        """
        :param obj: object to be plotted
        :param draw_params: optional parameters for plotting, overriding the parameters of the renderer
        :return: None
        """
        if draw_params is None:
            draw_params = self.draw_params.trajectory
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.trajectory

        if draw_params.time_begin >= draw_params.time_end:
            return

        traj_states = [obj.state_at_time_step(t) for t in range(draw_params.time_begin, draw_params.time_end) if
                       obj.state_at_time_step(t) is not None]
        position_sets = [s.position for s in traj_states if s.is_uncertain_position]
        traj_points = [s.position for s in traj_states if not s.is_uncertain_position]

        traj_points = np.array(traj_points)

        # Draw certain states
        if len(traj_points) > 0:
            if draw_params.draw_continuous:
                path = mpl.path.Path(traj_points, closed=False)
                self.obstacle_patches.append(
                    mpl.patches.PathPatch(path, color=draw_params.facecolor, lw=draw_params.line_width,
                                          zorder=draw_params.zorder, fill=False))
            else:
                self.dynamic_collections.append(
                    collections.EllipseCollection(np.ones([traj_points.shape[0], 1]) * draw_params.line_width,
                                                  np.ones([traj_points.shape[0], 1]) * draw_params.line_width,
                                                  np.zeros([traj_points.shape[0], 1]), offsets=traj_points,
                                                  offset_transform=self.ax.transData,
                                                  units='xy', linewidths=0, zorder=draw_params.zorder,
                                                  facecolor=draw_params.facecolor))

        # Draw uncertain states
        for pset in position_sets:
            pset.draw(self, draw_params.shape)

    def draw_trajectories(self, obj: List[Trajectory],
                          draw_params: OptionalSpecificOrAllDrawParams[TrajectoryParams] = None) -> None:
        if draw_params is None:
            draw_params = self.draw_params.trajectory
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.trajectory
        if draw_params.unique_colors:
            cmap = colormap_idx(len(obj))
            for i, traj in enumerate(obj):
                draw_params.facecolor = mpl.colors.to_hex(cmap(i))
                traj.draw(self, draw_params)
        else:
            self.draw_list(obj, draw_params)

    def draw_polygon(self, vertices, draw_params: OptionalSpecificOrAllDrawParams[ShapeParams] = None) -> None:
        """
        Draws a polygon shape

        :param vertices: vertices of the polygon
        :param draw_params: optional parameters for plotting, overriding the parameters of the renderer
        :return: None
        """
        if draw_params is None:
            draw_params = self.draw_params.shape
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.shape
        self.obstacle_patches.append(
            mpl.patches.Polygon(vertices, closed=True, facecolor=draw_params.facecolor, edgecolor=draw_params.edgecolor,
                                zorder=draw_params.zorder, alpha=draw_params.opacity, linewidth=draw_params.linewidth,
                                antialiased=draw_params.antialiased))

    def draw_rectangle(self, vertices: np.ndarray,
                       draw_params: OptionalSpecificOrAllDrawParams[ShapeParams] = None) -> None:
        """
        Draws a rectangle shape

        :param vertices: vertices of the rectangle
        :param draw_params: parameters for plotting given by a nested dict that
            recreates the structure of an object,
        :return: None
        """
        self.draw_polygon(vertices, draw_params)

    def draw_ellipse(self, center: Tuple[float, float], radius_x: float, radius_y: float,
                     draw_params: OptionalSpecificOrAllDrawParams[ShapeParams]) -> None:
        """
        Draws a circle shape

        :param ellipse: center position of the ellipse
        :param radius_x: radius of the ellipse along the x-axis
        :param draw_params: parameters for plotting given by a nested dict that
            recreates the structure of an object,
        :return: None
        """
        if draw_params is None:
            draw_params = self.draw_params.shape
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.shape
        self.obstacle_patches.append(
                mpl.patches.Ellipse(center, 2 * radius_x, 2 * radius_y, facecolor=draw_params.facecolor,
                                    edgecolor=draw_params.edgecolor, zorder=draw_params.zorder,
                                    linewidth=draw_params.linewidth, alpha=draw_params.opacity))


    def draw_state(self, state: State, draw_params: OptionalSpecificOrAllDrawParams[StateParams] = None) -> None:
        """
        Draws a state as an arrow of its velocity vector

        :param state: state to be plotted
        :param draw_params: optional parameters for plotting, overriding the parameters of the renderer
        :return: None
        """
        if draw_params is None:
            draw_params = self.draw_params.state
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.state

        zorder = draw_params.zorder
        if zorder is None:
            zorder = ZOrders.STATE
        self.obstacle_patches.append(
            mpl.patches.Circle(state.position, radius=draw_params.radius, zorder=zorder, color=draw_params.facecolor))

        if draw_params.draw_arrow:
            cos = math.cos(state.orientation)
            sin = math.sin(state.orientation)
            x = state.position[0]
            y = state.position[1]
            arrow_length = max(state.velocity, 3. / draw_params.scale_factor)
            self.obstacle_patches.append(
                    mpl.patches.FancyArrow(x=x, y=y, dx=arrow_length * cos * draw_params.scale_factor,
                                           dy=arrow_length * sin * draw_params.scale_factor, zorder=zorder,
                                           edgecolor=draw_params.arrow.edgecolor, facecolor=draw_params.arrow.facecolor,
                                           linewidth=draw_params.arrow.linewidth, width=draw_params.arrow.width))


    def draw_waters_network(self, obj: WatersNetwork, draw_params: Union[ParamServer, dict, None]) -> None:
        """
        Draws a waters network

        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict that
            recreates the structure of an object,
        :return: None
        """
        #TODO
        pass

    def draw_planning_problem_set(self, obj: PlanningProblemSet, draw_params: Union[ParamServer, dict, None]):
        """
        Draws all or selected planning problems from the planning problem set. Planning problems can be selected by
        providing IDs in`drawing_params[planning_problem_set][draw_ids]`

        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
            that recreates the structure of an object or a ParamServer object
        :return: None
        """

        if draw_params is None:
            draw_params = self.draw_params.planning_problem_set
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.planning_problem_set
        for pp_id, problem in obj.planning_problem_dict.items():
            if draw_params.draw_ids is None or pp_id in draw_params.draw_ids:
                self.draw_planning_problem(problem, draw_params.planning_problem)


    def draw_planning_problem(self, obj: PlanningProblem, draw_params: Union[ParamServer, dict, None]) -> None:
        """
        Draw initial state and goal region of the planning problem

        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
            that recreates the structure of an object or a ParamServer object
        :return: None
        """

        if draw_params is None:
            draw_params = self.draw_params.planning_problem
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.planning_problem
        self.draw_initital_state(obj.initial_state, draw_params.initial_state)
        self.draw_goal_region(obj.goal, draw_params.goal_region)

    def draw_initital_state(self, obj: State,
                            draw_params: OptionalSpecificOrAllDrawParams[InitialStateParams] = None) -> None:
        """
        Draw initial state with label

        :param obj: object to be plotted
        :param draw_params: optional parameters for plotting, overriding the parameters of the renderer
        :return: None
        """
        if draw_params is None:
            draw_params = self.draw_params.initial_state
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.initial_state

        obj.draw(self, draw_params.state)
        self.static_artists.append(
            text.Annotation(draw_params.label, xy=(obj.position[0] + 1, obj.position[1]), textcoords='data',
                            zorder=draw_params.label_zorder))

    def draw_goal_region(self, obj: GoalRegion,
                         draw_params: OptionalSpecificOrAllDrawParams[OccupancyParams] = None) -> None:
        """
        Draw goal states from goal region

        :param obj: object to be plotted
        :param draw_params: optional parameters for plotting, overriding the parameters of the renderer
        :return: None
        """
        if draw_params is None:
            draw_params = self.draw_params.goal_region
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.goal_region

        for goal_state in obj.state_list:
            self.draw_goal_state(goal_state, draw_params)

    def draw_label_with_position(self, label, positionx, positiony, widthoffset=None):

        usedoffset = 400 if widthoffset is None else widthoffset
        usedwidth = 30
        # usedoffset = 1.0
        # usedwidth = 20
        # if widthoffset:
        #    usedoffset = widthoffset* 40.9
        #    usedwidth = widthoffset *10
        # position = state.position
        # self.static_artists.append(
        #            text.Annotation(label, xy=(positionx + 10, positiony+10), textcoords='data', zorder=15))

        cutoffpointofx = self.plot_limits[1] - ((self.plot_limits[1] - self.plot_limits[0]) * 0.1)

        if not cutoffpointofx < positionx:
            # default pointer to the right

            if not self.plot_limits[3] - min(usedwidth * 40, 500) - 500 < positiony:
                # not close to big y boundary: goes in default positive y direction

                labelpos = positionx + usedoffset * 2, positiony + usedoffset
                self.dynamic_labels.append(text.Text(labelpos[0], labelpos[1], str(label), clip_on=True,
                                                     zorder=ZOrders.LABELS, horizontalalignment='left'))
                # self.dynamic_labels.append(text.Annotation(label, xy=(positionx + 10, positiony+10), textcoords='data', zorder=15))

                self.dynamic_labels.append(mpl.patches.FancyArrow(labelpos[0], labelpos[1], -usedoffset * 2 + usedwidth,
                                                                  -usedoffset + usedwidth, 0.03, False, 3.0, 3.0,
                                                                  'full', 0, False))
            else:
                #  close to big y boundary: to negative y direction
                labelpos = positionx + usedoffset * 2, positiony - usedoffset
                self.dynamic_labels.append(text.Text(labelpos[0], labelpos[1], str(label), clip_on=True,
                                                     zorder=ZOrders.LABELS, horizontalalignment='left'))
                self.dynamic_labels.append(mpl.patches.FancyArrow(labelpos[0], labelpos[1], -usedoffset * 2 + usedwidth,
                                                                  +usedoffset + usedwidth, 0.03, False, 3.0, 3.0,
                                                                  'full', 0, False))
                # self.dynamic_labels.append(text.Annotation(label, xy=(positionx + 10, positiony+10), textcoords='data', zorder=15))

        else:
            # pointer to the left, because we are close to the right border
            if not self.plot_limits[3] - min(usedwidth * 40, 500) - 500 < positiony:
                # not close to big y boundary: goes in default positive y direction

                labelpos = positionx - usedoffset * 5, positiony + usedoffset
                self.dynamic_labels.append(text.Text(labelpos[0], labelpos[1], str(label), clip_on=True,
                                                     zorder=ZOrders.LABELS, horizontalalignment='right'))
                self.dynamic_labels.append(mpl.patches.FancyArrow(labelpos[0], labelpos[1], +usedoffset * 2 + usedwidth,
                                                                  -usedoffset + usedwidth, 0.03, False, 3.0, 3.0,
                                                                  'full', 0, False))
                # self.dynamic_labels.append(text.Annotation(label, xy=(positionx + 10, positiony+10), textcoords='data', zorder=15))

            else:
                #  close to big y boundary: to negative y direction
                labelpos = positionx - usedoffset * 5, positiony - usedoffset
                self.dynamic_labels.append(text.Text(labelpos[0], labelpos[1], str(label), clip_on=True,
                                                     zorder=ZOrders.LABELS, horizontalalignment='right'))
                self.dynamic_labels.append(mpl.patches.FancyArrow(labelpos[0], labelpos[1], +usedoffset * 2 + usedwidth,
                                                                  +usedoffset + usedwidth, 0.03, False, 3.0, 3.0,
                                                                  'full', 0, False))
                # self.dynamic_labels.append(text.Annotation(label, xy=(positionx + 10, positiony+10), textcoords='data', zorder=15))

        #        self._plot_limits
        # [min_x, max_x, min_y, max_y]

        # self.static_artists.append(
        #            text.Annotation(label, xy=(positionx + 10, positiony+10), textcoords='data', zorder=15))

    def draw_goal_state(self, obj: State,
                        draw_params: OptionalSpecificOrAllDrawParams[OccupancyParams] = None) -> None:
        """
        Draw goal states

        :param obj: object to be plotted
        :param draw_params: optional parameters for plotting, overriding the parameters of the renderer
        :return: None
        """
        if draw_params is None:
            draw_params = self.draw_params.goal_region
        elif isinstance(draw_params, MPDrawParams):
            draw_params = draw_params.goal_region

        if hasattr(obj, 'position'):
            if type(obj.position) == list:
                for pos in obj.position:
                    pos.draw(self, draw_params.shape)
            else:
                obj.position.draw(self, draw_params.shape)


