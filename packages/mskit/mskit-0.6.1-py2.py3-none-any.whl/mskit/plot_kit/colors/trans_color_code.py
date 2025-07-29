import numpy as np

__all__ = [
    "hex_to_rgb",
    "rgb_to_hex",
    "hsl_to_rgb",
    "rgb_to_hsl",
    "hue_to_rgb",
]


def hex_to_rgb(hex_color, base=256):
    return tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))


def rgb_to_hex(rgb, rgb_base=255, with_sharp=True, upper=True):
    # Check channel num to be 3
    channel_num = len(rgb)
    if channel_num != 3:
        raise ValueError(f"The input rgb value {rgb} need three channels, now has {channel_num}")

    # Trans each rgb channel to 255 based number
    if rgb_base != 255:
        rgb = [int(one_channel * 255 / rgb_base) for one_channel in rgb]

    # Trans to hex code and check if length of hex code is 1
    hex_list = [hex(one_channel)[2:] for one_channel in rgb]
    for i in range(channel_num):
        if len(hex_list[i]) == 1:
            hex_list[i] = f"0{hex_list[i]}"

    # Join hex codes to full hex color
    hex_code = "".join(hex_list)
    if with_sharp:
        hex_code = f"#{hex_code}"
    if upper:
        hex_code = hex_code.upper()
    return hex_code


def hsl_to_rgb(hsl, h_type="degree"):
    h, s, l = hsl
    if h_type == "degree":
        h /= 360
    if hsl[1] == 0:
        rgb = [_ * 255 for _ in hsl]
    else:
        if l < 0.5:
            value_2 = l * (s + 1)
        else:
            value_2 = (s + l) - s * l
        value_1 = 2 * l - value_2
        rgb = [255 * hue_to_rgb(value_1, value_2, h + _ / 3) for _ in range(1, -2, -1)]
    for i, one_rgb in enumerate(rgb):
        if one_rgb % 1 > 0.999:
            rgb[i] += 1
    return [int(_) for _ in rgb]


def rgb_to_hsl(x, h_type="degree"):
    norm_rgb = np.array(x) / 255
    min_value = norm_rgb.min()
    max_value = norm_rgb.max()
    delta_value = max_value - min_value
    l = (min_value + max_value) / 2
    if delta_value == 0:
        h = 0
        s = 0
    else:
        if l < 0.5:
            s = delta_value / (min_value + max_value)
        else:
            s = delta_value / (2 - min_value - max_value)
        delta_rgb = (((max_value - norm_rgb) / 6) + (delta_value / 2)) / delta_value

        max_channel_idx = norm_rgb.argmax()
        sec_calc_index = max_channel_idx + 1 if max_channel_idx < 2 else 0
        h = max_channel_idx / 3 + delta_rgb[max_channel_idx - 1] - delta_rgb[sec_calc_index]

        if h < 0:
            h += 1
        elif h > 1:
            h -= 1
    if h_type == "degree":
        return h * 360, s, l
    elif h_type == "decimal":
        return h, s, l
    else:
        raise


def hue_to_rgb(value_1, value_2, hue):
    if hue < 0:
        hue += 1
    elif hue > 1:
        hue -= 1
    if hue < 1 / 6:
        return value_1 + (value_2 - value_1) * 6 * hue
    elif hue < 1 / 2:
        return value_2
    elif hue < 2 / 3:
        return value_1 + (value_2 - value_1) * (2 / 3 - hue) * 6
    else:
        return value_1


def rgb_to_hue():
    pass


def trans_color_code(input_=None, from_="", to_="", *args):
    pass
