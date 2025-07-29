import numpy as np

from .trans_color_code import rgb_to_hsl, hsl_to_rgb


def gradient_hsl(start, end, number, input_color_type="rgb", output_color_type="rgb", value_scale=None):
    if number < 2:
        raise
    if input_color_type.lower() != "rgb":
        raise

    colors = np.array(
        [np.linspace(*each_channel, number) for each_channel in zip(rgb_to_hsl(start), rgb_to_hsl(end))]
    ).transpose()

    if output_color_type.lower() == "rgb":
        colors = [hsl_to_rgb(_) for _ in colors]
    if value_scale:
        colors = [[__ / value_scale for __ in _] for _ in colors]
    return colors


def gradient_rgb(start, end, number, input_color_type="rgb", output_color_type="rgb", value_scale=None):
    if number < 2:
        raise
    if input_color_type.lower() != "rgb":
        raise

    colors = np.array([np.linspace(*each_channel, number) for each_channel in zip(start, end)]).transpose()
    colors = colors.astype(int)
    if value_scale:
        colors = [[__ / value_scale for __ in _] for _ in colors]
    return colors
