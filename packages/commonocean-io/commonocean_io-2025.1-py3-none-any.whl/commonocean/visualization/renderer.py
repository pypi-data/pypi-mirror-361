from abc import ABCMeta, abstractmethod

__author__ = "Hanna Krasowski"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"


class IRenderer(metaclass=ABCMeta):
    @abstractmethod
    def draw_scenario(self, obj, draw_params):
        """
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    def draw_waters_traffic_sign(self, obj, draw_params):
        """
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_static_obstacle(self, obj, draw_params):
        """
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_dynamic_obstacle(self, obj, draw_params):
        """
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass


    @abstractmethod
    def draw_trajectory(self, obj, draw_params):
        """
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_trajectories(self, obj, draw_params):
        pass

    @abstractmethod
    def draw_polygon(self, vertices, draw_params):
        """
        Draws a polygon shape
        :param vertices: vertices of the polygon
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_rectangle(self, vertices, draw_params):
        """
        Draws a rectangle shape
        :param vertices: vertices of the rectangle
        :param draw_params: parameters for plotting given by a nested dict that
        recreates the structure of an object,
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_ellipse(self, center, radius_x, radius_yt, draw_params):
        """
        Draws a circle shape
        :param ellipse: center position of the ellipse
        :param radius_x: radius of the ellipse along the x-axis
        :param radius_y: radius of the ellipse along the y-axis
        :param draw_params: parameters for plotting given by a nested dict that
        recreates the structure of an object,
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_state(self, state, draw_params):
        """
        Draws a state as an arrow of its velocity vector
        :param state: state to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_goal_region(self, obj, draw_params):
        """
        Draw goal states from goal region
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_planning_problem(self, obj, draw_params):
        """
        Draw initial state and goal region of the planning problem
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_planning_problem_set(self, obj, draw_params):
        """
        Draws all or selected planning problems from the planning problem
        set. Planning problems can be selected by providing IDs in
        `drawing_params[planning_problem_set][draw_ids]`
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_initital_state(self, obj, draw_params):
        """
        Draw initial state with label
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

    @abstractmethod
    def draw_goal_state(self, obj, draw_params):
        """
        Draw goal states
        :param obj: object to be plotted
        :param draw_params: parameters for plotting given by a nested dict
        that recreates the structure of an object or a ParamServer object
        :param call_stack: tuple of string containing the call stack,
        which allows for differentiation of plotting styles
               depending on the call stack
        :return: None
        """
        pass

