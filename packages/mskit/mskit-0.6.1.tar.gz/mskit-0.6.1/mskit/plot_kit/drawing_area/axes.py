from typing import Optional, Sequence, Union

import matplotlib.pyplot as plt
import numpy as np


def init_container(container=None, **fig_args):
    if container is None:
        container = plt.figure(*fig_args)
    if isinstance(container, plt.Figure):
        new_ax_method = container.add_axes
    elif isinstance(container, plt.Axes):
        new_ax_method = container.inset_axes
    else:
        raise ValueError(f"container should be `Figure` or `Axes` or `None`, now {type(container)}")
    return container, new_ax_method


def init_isometric_axes(
    left_init=0.05,
    bottom_init=0.05,
    right_end=0.9,
    top_end=0.9,
    ax_col_gap=0.1,
    ax_row_gap=0.1,
    row_num=2,
    col_num=5,
    total_num=None,
    container=None,
    **fig_args,
):  # TODO support new ax args
    container, new_ax_method = init_container(container=container, **fig_args)

    if isinstance(ax_col_gap, (float, int)):
        ax_col_gap = [ax_col_gap] * (col_num - 1)
    if isinstance(ax_row_gap, (float, int)):
        ax_row_gap = [ax_row_gap] * (row_num - 1)
    else:
        ax_row_gap = ax_row_gap[::-1]
    if not total_num:
        total_num = row_num * col_num

    fig_length = right_end - left_init
    fig_height = top_end - bottom_init

    row_height = (fig_height - sum(ax_row_gap)) / row_num
    col_length = (fig_length - sum(ax_col_gap)) / col_num

    ax_x = [left_init + sum(ax_col_gap[:i]) + col_length * i for i in range(col_num)]
    ax_y = [top_end - sum(ax_row_gap[:i]) - row_height * (i + 1) for i in range(row_num)]

    ax_num = 0
    axes_list = []
    for row_index, y in enumerate(ax_y):
        for col_index, x in enumerate(ax_x):
            if ax_num == total_num:
                break
            ax = new_ax_method([x, y, col_length, row_height])
            axes_list.append(ax)
            ax_num += 1

    return container, axes_list


def init_weighted_axes(
    x_start=0.05,
    x_end=0.9,
    y_start=0.05,
    y_end=0.9,
    col_weight: Union[float, Sequence[float]] = 1,
    col_gap: Union[float, Sequence[float]] = 0.1,
    col_num: Optional[int] = None,
    row_weight: Union[float, Sequence[float]] = 1,
    row_gap: Union[float, Sequence[float]] = 0.1,
    row_num: Optional[int] = None,
    axes_names: Optional[Sequence[str]] = None,
    container: Optional[Union[plt.Figure, plt.Axes]] = None,
    **fig_args,
):
    """
    note: rows are counted from the bottom to the top, and columns are counted from the left to the right
    axes_names  # list of names for all generated axes (row * col), or two tuples in list to boardcast to a matrix
    sharex: 'all', 'col', `[(1, 3, 5), (0, 2)]`, `2/2-2/4;3/1-3/3;2/0-2/1`
    """
    container, new_ax_method = init_container(container=container, **fig_args)

    if isinstance(col_weight, (float, int)):
        if col_num is None:
            col_weight = [col_weight]
        else:
            col_weight = [col_weight] * col_num
    col_num = len(col_weight)
    if isinstance(col_gap, (float, int)):
        col_gap = [col_gap] * (col_num - 1)
    else:
        if len(col_gap) != (col_num - 1):
            raise ValueError(f"col_gap should be a float or a list of floats with length {col_num - 1}")

    col_space_total = x_end - x_start
    required_col_space = sum(col_weight) + sum(col_gap)
    col_weight = col_space_total / required_col_space * np.asarray(col_weight)
    col_gap = col_space_total / required_col_space * np.asarray(col_gap)
    col_x_start = [x_start + sum(col_gap[:i]) + sum(col_weight[:i]) for i in range(col_num)]

    if isinstance(row_weight, (float, int)):
        if row_num is None:
            row_weight = [row_weight]
        else:
            row_weight = [row_weight] * row_num
    row_num = len(row_weight)
    if isinstance(row_gap, (float, int)):
        row_gap = [row_gap] * (row_num - 1)
    else:
        if len(row_gap) != (row_num - 1):
            raise ValueError(f"row_gap should be a float or a list of floats with length {row_num - 1}")

    row_space_total = y_end - y_start
    required_row_space = sum(row_weight) + sum(row_gap)
    row_weight = row_space_total / required_row_space * np.asarray(row_weight)
    row_gap = row_space_total / required_row_space * np.asarray(row_gap)
    row_y_start = [y_start + sum(row_gap[:i]) + sum(row_weight[:i]) for i in range(row_num)]

    axes_list = []
    for row_index, y in enumerate(row_y_start):
        axes_list.append([])
        for col_index, x in enumerate(col_x_start):
            ax = new_ax_method([x, y, col_weight[col_index], row_weight[row_index]])
            axes_list[-1].append(ax)
    if len(axes_list) == 1:
        axes_list = axes_list[0]
    return container, axes_list
