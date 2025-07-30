import dataclasses
import inspect
from dataclasses import dataclass, field
import pathlib
from typing import Any, Optional, Dict, TypeVar, Union, List

from omegaconf import OmegaConf

__author__ = "Hanna Krasowski"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"

Color = str

def _dict_to_params(dict_params, cls):
    fields = dataclasses.fields(cls)
    cls_map = {f.name: f.type for f in fields}
    kwargs = {}
    for k, v in cls_map.items():
        if k not in dict_params:
            continue
        if inspect.isclass(v) and issubclass(v, ParamServer):
            kwargs[k] = _dict_to_params(dict_params[k], cls_map[k])
        else:
            kwargs[k] = dict_params[k]
    return cls(**kwargs)


@dataclass
class ParamServer:
    #: First time step of the visualized time interval.
    time_begin: int = 0
    #: Last time step of the visualized time interval.
    time_end: int = 200
    #: Use anti-aliasing.
    antialiased: bool = True
    __initialized: bool = field(init=False, default=False, repr=False)

    def __post_init__(self):
        self.__initialized = True
        # Make sure that the base parameters are propagated to all sub-parameters
        # This cannot be done in the init method, because the sub-parameters are not yet initialized.
        # This is not a noop, as it calls the __setattr__ method.
        # Do not remove!
        self.time_begin = self.time_begin
        self.time_end = self.time_end
        self.antialiased = self.antialiased

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {f.name for f in dataclasses.fields(self)}:
            super().__setattr__(name, value)
        if self.__initialized:
            for k, v in self.__dict__.items():
                if isinstance(v, ParamServer):
                    v.__setattr__(name, value)

    def __getitem__(self, item):
        try:
            value = self.__getattribute__(item)
        except AttributeError:
            raise KeyError(f"{item} is not a parameter of {self.__class__.__name__}")
        return value

    def __setitem__(self, key, value):
        try:
            self.__setattr__(key, value)
        except AttributeError:
            raise KeyError(f"{key} is not a parameter of {self.__class__.__name__}")

    @classmethod
    def load(cls, file_path: Union[pathlib.Path, str], validate_types: bool = True):
        file_path = pathlib.Path(file_path)
        assert file_path.suffix == ".yaml", f"File type {file_path.suffix} is unsupported! Please use .yaml!"
        loaded_yaml = OmegaConf.load(file_path)
        if validate_types:
            OmegaConf.merge(OmegaConf.structured(MPDrawParams), loaded_yaml)
        params = _dict_to_params(OmegaConf.to_object(loaded_yaml), cls)
        return params

    def save(self, file_path: Union[pathlib.Path, str]):
        # Avoid saving private attributes
        dict_cfg = dataclasses.asdict(self, dict_factory=lambda items: {key: val for key, val in items if
                                                                        not key.startswith("_")})
        OmegaConf.save(OmegaConf.create(dict_cfg), file_path, resolve=True)


@dataclass
class ShapeParams(ParamServer):
    opacity: float = 1.0
    facecolor: Color = "#1d7eea"
    edgecolor: Color = "#00478f"
    linewidth: float = 0.5
    zorder: float = 20
    # draw mesh of Polygon
    # NOTE: This parameter is currently only valid for Collision Polygons created by the CommonRoad-Drivability-Checker
    # and has no effect for the Polygon class defined in commonroad-io.geometry.shape
    draw_mesh: bool = False


@dataclass
class ArrowParams(ParamServer):
    linewidth: float = 1.5
    edgecolor: Color = "black"
    facecolor: Color = "black"
    width: float = 0.8


@dataclass
class StateParams(ParamServer):
    draw_arrow: bool = False
    radius: float = 0.5
    scale_factor: float = 0.3
    linewidth: Optional[float] = None
    edgecolor: Optional[Color] = "black"
    facecolor: Optional[Color] = "black"
    zorder: float = 25
    arrow: ArrowParams = field(default_factory=ArrowParams)


@dataclass
class OccupancyParams(ParamServer):
    draw_occupancies: bool = True
    shape: ShapeParams = field(default_factory=lambda: ShapeParams(zorder=18, opacity=0.2))
    uncertain_position: ShapeParams = field(
            default_factory=lambda: ShapeParams(opacity=0.6, facecolor="#000000", edgecolor="#000000"))


@dataclass
class HistoryParams(ParamServer):
    """Draw the history of an object with fading colors."""
    draw_history: bool = False
    steps: int = 5
    step_size: int = 1
    fade_color: float = 0.1
    basecolor: Color = "#ffe119"
    occupancy: ShapeParams = field(
            default_factory=lambda: ShapeParams(opacity=0.2, edgecolor="k", linewidth=0.0, zorder=17))


@dataclass
class StaticObstacleParams(ParamServer):
    occupancy: OccupancyParams = field(
            default_factory=lambda: OccupancyParams(shape=ShapeParams(facecolor="#d95558", edgecolor="#831d20")))

@dataclass
class TrajectoryParams(ParamServer):
    draw_trajectory: bool = True
    facecolor: Color = "#000000"
    #: Draw trajectories as a continuous line instead of dots.
    draw_continuous: bool = False
    line_width: float = 0.17
    #: Use unique colors for each of the trajectories points.
    unique_colors: bool = False
    #: Parameters for shapes of uncertain position.
    shape: ShapeParams = field(default_factory=lambda: ShapeParams(facecolor="#000000", edgecolor="#000000", zorder=24))
    zorder: float = 24


@dataclass
class InitialStateParams(ParamServer):
    label_zorder: float = 35
    label: str = ""
    state: StateParams = field(
            default_factory=lambda: StateParams(draw_arrow=True, radius=1.0, scale_factor=0.5, facecolor="#000080", zorder=11,
                                                arrow=ArrowParams(facecolor="#000080", edgecolor="#000080")))


@dataclass
class PlanningProblemParams(ParamServer):
    initial_state: InitialStateParams = field(default_factory=InitialStateParams)
    goal_region: OccupancyParams = field(
        default_factory=lambda: OccupancyParams(shape=ShapeParams(facecolor="#f1b514", edgecolor="#000080", zorder=15)))


@dataclass
class PlanningProblemSetParams(ParamServer):
    #: Limit planning problems to a list of IDs, or None to include all IDs.
    draw_ids: Optional[List[int]] = None
    planning_problem: PlanningProblemParams = field(default_factory=PlanningProblemParams)


@dataclass
class VesselShapeParams(ParamServer):
    #: Options for visualizing the direction indicator of the vehicle shape.
    direction: ShapeParams = field(default_factory=lambda: ShapeParams(facecolor="#000000"))
    #: Options for visualizing the vehicle's occupancy in the current time step.
    occupancy: OccupancyParams = field(
            default_factory=lambda: OccupancyParams(shape=ShapeParams(opacity=1.0, zorder=20, facecolor="#000000")))


@dataclass
class DynamicObstacleParams(ParamServer):
    draw_shape: bool = True
    #: Draw a type-dependent icon (if available) instead of the primitive geometric shape.
    draw_icon: bool = False
    #: Draw the direction indicator of the dynamic obstacle.
    draw_direction: bool = False
    draw_bounding_box: bool = True
    #: Show the ID of the dynamic obstacle.
    show_label: bool = False
    #: Visualize the dynamic obstacle signals like indicator or braking lights.
    draw_signals: bool = True
    #: Draw the initial state of the dynamic obstacle.
    draw_initial_state: bool = False
    #: Options for visualizing the vehicle in the current time step.
    vessel_shape: VesselShapeParams = field(default_factory=VesselShapeParams)
    #: Options for visualizing the vehicle states within [time_begin, time_end].
    state: StateParams = field(default_factory=StateParams)
    #: Options for visualizing the vehicle occupancy history with fading colors.
    history: HistoryParams = field(default_factory=HistoryParams)
    #: Options for visualizing the vehicle occupancy in future time steps.
    occupancy: OccupancyParams = field(default_factory=OccupancyParams)
    #: Options for visualizing the vehicle trajectory in future time steps.
    trajectory: TrajectoryParams = field(default_factory=TrajectoryParams)



@dataclass
class MPDrawParams(ParamServer):
    #: Enable axes for matplotlib.
    axis_visible: bool = True
    shape: ShapeParams = field(default_factory=ShapeParams)
    dynamic_obstacle: DynamicObstacleParams = field(default_factory=DynamicObstacleParams)
    static_obstacle: StaticObstacleParams = field(default_factory=StaticObstacleParams)
    trajectory: TrajectoryParams = field(default_factory=TrajectoryParams)
    occupancy: OccupancyParams = field(default_factory=OccupancyParams)
    state: StateParams = field(default_factory=StateParams)
    planning_problem: PlanningProblemParams = field(default_factory=PlanningProblemParams)
    planning_problem_set: PlanningProblemSetParams = field(default_factory=PlanningProblemSetParams)
    initial_state: InitialStateParams = field(default_factory=InitialStateParams)
    goal_region: OccupancyParams = field(default_factory=OccupancyParams)


T = TypeVar("T")
OptionalSpecificOrAllDrawParams = Optional[Union[T, MPDrawParams]]
