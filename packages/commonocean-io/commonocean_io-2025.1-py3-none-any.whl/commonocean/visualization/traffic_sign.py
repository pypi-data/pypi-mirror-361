import copy
import enum
import os
from collections import defaultdict, OrderedDict
from typing import Dict, Callable, Tuple, Union, Any,List
import matplotlib as mpl
import matplotlib.patches as patches
import matplotlib.collections as collections
from PIL import Image

import commonroad.prediction.prediction
import commonocean.scenario.obstacle
import commonocean.visualization.draw_dispatch_cr
from commonroad.geometry.shape import *
from commonocean.scenario.traffic_sign import TrafficSign
from matplotlib.offsetbox import OffsetImage, \
    AnnotationBbox, \
    HPacker, \
    TextArea, \
    VPacker, \
    OffsetBox

# Tunneling from CR-IO #
from commonroad.visualization.traffic_sign import isfloat as isfloat_CR
from commonroad.visualization.traffic_sign import rescale_text as rescale_text_CR
########################

__author__ = "Hanna Krasowski, Benedikt Pfleiderer, Fabian Thomas-Barein"
__copyright__ = "TUM Cyber-Physical System Group"
__credits__ = ["ConVeY"]
__version__ = "2022a"
__maintainer__ = "Hanna Krasowski"
__email__ = "commonocean@lists.lrz.de"
__status__ = "released"

traffic_sign_path = os.path.join(os.path.dirname(__file__), 'traffic_signs/')

def isfloat(value: str):
    return isfloat_CR(value)

def text_prop_dict() -> dict:
    """Properties of text for additional_value."""
    return {
            '274':     {
                    'mpl_args':          {'weight': 'bold', 'size': 13.5},
                    'rescale_threshold': 2,
                    'position_offset':   -21.0
            }, '275':  {
                    'mpl_args':             {
                            'weight': 'bold', 'color': 'white', 'size': 13.5
                    }, 'rescale_threshold': 2, 'position_offset': -21.0
            }, '278':  {
                    'mpl_args':           {
                            'weight': 'bold', 'color': 'gray', 'size': 10
                    }, 'position_offset': -16.5
            }, '279':  {
                    'mpl_args':           {
                            'weight': 'bold', 'color': 'white', 'size': 10
                    }, 'position_offset': -16.5
            }, '310':  {
                    'mpl_args': {
                            'weight': 'normal', 'color': 'black', 'size': 10
                    }
            }, '380':  {
                    'mpl_args':           {
                            'weight': 'bold', 'color': 'white', 'size': 10
                    }, 'position_offset': -16.5
            }, '381':  {
                    'mpl_args':           {
                            'weight': 'bold', 'color': 'white', 'size': 10
                    }, 'position_offset': -16.5
            }, 'R2-1': {
                    'mpl_args':           {
                            'weight': 'normal', 'color': 'black', 'size': 10.5
                    }, 'position_offset': -13.5
            }
    }


def rescale_text(string: str, prop: dict, scale_factor: float,
                 default_scale_factor: float) -> dict:
    """Rescales text size proportionally to the max. number of strings given
    by prop['rescale_threshold'] and to the
    'scale_factor' compared to the default scale_factor. Used e.g. for
    fitting speed limits into the traffic sign."""
    
    return rescale_text_CR(string, prop, scale_factor, default_scale_factor)


def create_img_boxes_traffic_sign(
        traffic_signs: Union[List[TrafficSign], TrafficSign], draw_params: dict,
        call_stack: Tuple[str, ...]) -> Dict[
    Tuple[float, float], List[OffsetBox]]:
    """
    For each Traffic sign an OffsetBox is created, containing the png image
    and optionally labels. These boxes can
    be stacked horizontally later when multiple signs share the
    same position.
    :param traffic_signs:
    :param draw_params:
    :param call_stack:
    :return:
    """
    if type(traffic_signs) is not list:
        traffic_signs = [traffic_signs]

    if len(traffic_signs) == 0:
        return dict()

    scale_factor = commonocean.visualization.draw_dispatch_cr\
        ._retrieve_alternate_value(
            draw_params, call_stack, ('traffic_sign', 'scale_factor'),
            ('scenario', 'waters_network', 'traffic_sign', 'scale_factor'))
    show_label_default = commonocean.visualization.draw_dispatch_cr\
        ._retrieve_alternate_value(
            draw_params, call_stack, ('traffic_sign', 'show_label'),
            ('scenario', 'waters_network', 'traffic_sign', 'show_label'))
    show_traffic_signs = commonocean.visualization.draw_dispatch_cr\
        ._retrieve_alternate_value(
            draw_params, call_stack, ('traffic_sign', 'show_traffic_signs'), (
                    'scenario', 'waters_network', 'traffic_sign',
                    'show_traffic_signs'))
    zorder = commonocean.visualization.draw_dispatch_cr\
        ._retrieve_alternate_value(
            draw_params, call_stack, ('traffic_sign', 'zorder'),
            ('scenario', 'waters_network', 'traffic_sign', 'zorder'))

    scale_factor_default = commonocean.visualization.draw_dispatch_cr\
        ._retrieve_value(
            commonocean.visualization.draw_dispatch_cr.default_draw_params,
            call_stack,
            ('scenario', 'waters_network', 'traffic_sign', 'scale_factor'))

    assert any([show_traffic_signs == 'all',
                isinstance(show_traffic_signs, list) and type(
                        show_traffic_signs[0] is enum)]), 'Plotting option ' \
                                                          'traffic_sign.show_traffic_signs must ' \
                                                          'be either "all" or ' \
                                                          'list of type ' \
                                                          'TrafficSignID'

    prop_dict = text_prop_dict()
    imageboxes_all = defaultdict(list)

    for traffic_sign in traffic_signs:
        if traffic_sign.virtual is True or traffic_sign.position is None:
            continue
        imageboxes = []
        for element in traffic_sign.traffic_sign_elements:
            el_id = element.traffic_sign_element_id
            if not (show_traffic_signs == 'all' or el_id in show_traffic_signs):
                continue
            show_label = show_label_default
            path = os.path.join(traffic_sign_path, el_id.value + '.png')
            plot_img = True

            if not os.path.exists(path):
                show_label = True
                warnings.warn(
                        'No png file for traffic sign id {} exists under '
                        'path '
                        '{}, skipped plotting.'.format(el_id, path))
                plot_img = False

            boxes = []
            if show_label:
                boxes.append(TextArea(el_id.name))

            if plot_img:
                sign_img = Image.open(path)
                boxes.append(
                        OffsetImage(sign_img, zoom=scale_factor, zorder=zorder,
                                    interpolation='bicubic'))

            if len(boxes) > 1:
                boxes = [VPacker(children=boxes, pad=0, sep=0, align='center')]

            sep = 0
            if len(element.additional_values) > 0:

                add_text = '\n'.join(element.additional_values)

                props = prop_dict[
                    el_id.value] if el_id.value in prop_dict else {
                        'mpl_args': {}
                }
                props = rescale_text(add_text, props, scale_factor,
                                     scale_factor_default)
                boxes.append(TextArea(add_text, textprops=props['mpl_args']))

                if plot_img and 'position_offset' in props:
                    sep = props['position_offset']

            img = VPacker(children=boxes, pad=0, sep=sep, align='center')
            imageboxes.append(img)

        if len(imageboxes) > 0:
            hbox = HPacker(children=imageboxes, pad=0, sep=0.05,
                           align='baseline')
            imageboxes_all[tuple(traffic_sign.position.tolist())].append(hbox)

    return imageboxes_all



def draw_traffic_light_signs(traffic_lights_signs: Union[
    List[Union[TrafficSign]], Union[TrafficSign]],
                             plot_limits: Union[List[Union[int, float]], None],
                             ax: mpl.axes.Axes, draw_params: dict,
                             draw_func: Dict[type, Callable], handles: Dict[
            Any, List[Union[mpl.patches.Patch, mpl.collections.Collection]]],
                             call_stack: Tuple[str, ...]) -> None:
    """
    Draws OffsetBoxes which are first collected for all traffic signs and
    -lights. Boxes are stacked together when they
    share the same position.
    :param traffic_lights_signs:
    :param plot_limits:
    :param ax:
    :param draw_params:
    :param draw_func:
    :param handles:
    :param call_stack:
    :return:
    """
    kwargs = commonocean.visualization.draw_dispatch_cr\
        ._retrieve_alternate_value(
            draw_params, call_stack, ('kwargs_traffic_light_signs',),
            ('scenario', 'waters_network', 'kwargs_traffic_light_signs'))

    zorder_1 = commonocean.visualization.draw_dispatch_cr\
        ._retrieve_alternate_value(
            draw_params, call_stack, ('traffic_sign', 'zorder'),
            ('scenario', 'waters_network', 'traffic_sign', 'zorder'))

    zorder = zorder_1
    threshold_grouping = 0.8 

    if not isinstance(traffic_lights_signs, list):
        traffic_lights_signs = [traffic_lights_signs]

    traffic_signs = []

    for obj in traffic_lights_signs:
        if isinstance(obj, TrafficSign):
            traffic_signs.append(obj)
        else:
            warnings.warn('Object of type {}, but expected type TrafficSign'.format(type(obj)))

    boxes_signs = create_img_boxes_traffic_sign(traffic_signs, draw_params,
                                                call_stack)
    img_boxes = defaultdict(list) 
    [img_boxes[pos].extend(box_list) for pos, box_list in boxes_signs.items()]

    if not img_boxes:
        return None

    positions = list(img_boxes.keys())
    box_lists = list(img_boxes.values())

    groups = dict()
    grouped = set()  
    i = 1
    for pos, box_list in zip(positions[:-1], box_lists[:-1]):
        i += 1
        group_tmp = list(box_list)
        if pos in grouped:
            continue
        gr_pos_tmp = [np.array(pos)]
        for pos2, box_list2 in zip(positions[i:], box_lists[i:]):
            if pos2 in grouped:
                continue
            if np.linalg.norm(np.array(pos) - np.array(pos2),
                              ord=np.inf) < threshold_grouping:
                group_tmp.extend(box_list2)
                gr_pos_tmp.append(np.array(pos2))

        grouped.add(pos)
        groups[tuple(np.average(gr_pos_tmp, axis=0).tolist())] = group_tmp

    if positions[-1] not in grouped:
        groups[positions[-1]] = box_lists[-1]

    default_params = dict(xycoords='data', frameon=False)
    for param, value in default_params.items():
        if param not in kwargs:
            kwargs[param] = value

    for position_tmp, box_list_tmp in groups.items():
        position_tmp = np.array(position_tmp)
        kwargs_tmp = copy.deepcopy(kwargs)
        if 'xybox' not in kwargs_tmp:
            kwargs_tmp['xybox'] = position_tmp

        hbox = HPacker(children=box_list_tmp, pad=0, sep=0.1, align='baseline')
        ab = AnnotationBbox(hbox, position_tmp, **kwargs_tmp)
        ab.zorder = zorder
        ax.add_artist(ab)