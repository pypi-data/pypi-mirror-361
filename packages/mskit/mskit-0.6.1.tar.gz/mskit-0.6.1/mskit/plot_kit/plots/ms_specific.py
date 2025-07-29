import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import pearsonr

from mskit.plot_kit.colors.preferred_colors import S
from mskit.plot_kit.drawing_area.ax_utls import set_thousand_separate
from mskit.stats import delta_tx_to_rt_2diff, r_square


def pcc_hist(
    pcc_list,
    bin_num=18,
    bin_color="#696969",
    bin_alpha=0.75,
    median_line=True,
    median_color="#009ACD",
    median_width=3,
    percent_list=(90, 80, 70),
    label_fontsize=8,
    anno_fontsize=8,
    anno_y_site=(0.75, 0.5, 0.4),
    anno_metric_name="PCC",
    x_lim=(0, 1),
    data_warning=False,
    x_label="PCC",
    y_label="Number of test peptide precursors",
    title=None,
    ax=None,
    save=None,
):
    # TODO Other metric like SA in annotation
    # TODO Value of metric with certain percentage

    # TODO Check data (e.g. NA values)
    if ax is None:
        ax = plt.gca()

    pcc_list = np.array(pcc_list)
    median_pcc = np.median(pcc_list)
    pcc_num = len(pcc_list)

    set_thousand_separate(ax, axis=("y",))

    ax.set_xlim(*x_lim)
    ax.set_xticks(np.linspace(0, 1, 6))

    hist = ax.hist(pcc_list, bins=bin_num, alpha=bin_alpha, color=bin_color, edgecolor="k")

    if median_line:
        mid_line = ax.axvline(median_pcc, linewidth=median_width, color=median_color)
    else:
        mid_line = None

    ax.set_xlabel(x_label, fontsize=label_fontsize)
    ax.set_ylabel(y_label, fontsize=label_fontsize)

    percent_list = sorted(map(lambda x: x / 100, percent_list))
    pcc_percent_list = []
    anno_title = f">{anno_metric_name} Percentage"
    pcc_anno_list = [anno_title]
    for pcc in percent_list:
        ratio = np.sum(pcc_list > pcc) / pcc_num
        pcc_percent_list.append(ratio)
        pcc_anno_list.append(f">{pcc:.2f}  {ratio:.1%}")

    ax.annotate("\n".join(pcc_anno_list), xy=(0.05, ax.get_ylim()[1] * anno_y_site[0]), fontsize=anno_fontsize)
    ax.annotate(
        "Median {}: {:.3f}".format(anno_metric_name, median_pcc),
        xy=(0.05, ax.get_ylim()[1] * anno_y_site[1]),
        fontsize=anno_fontsize,
    )
    ax.annotate(r"n = {:,}".format(pcc_num), xy=(0.05, ax.get_ylim()[1] * anno_y_site[2]), fontsize=anno_fontsize)

    if title:
        ax.set_title(title)

    if save:
        plt.savefig(save + f".{anno_metric_name}.png")

    return hist, mid_line, pcc_anno_list


# TODO Reg class
"""
将绘制函数放在 class 中还是独立的函数中？

class XXX:
    def __init__(xxxxx)
        self.figure = None
        self.ax = None
        self.data = None
    def draw(xxxxx):


def rt_reg(Other_Params=None, ..., XXX=None):
    if XXX=None:
        x = XXX(....)
        x.draw()
        return x
    else:
        x = XXX
        update x param
        x.draw()
        return x
"""


def define_reg_ax(ax, rt_1, rt_2, x_label, y_label, rt_unit, expand=0.2):
    rt_range = (min(min(rt_1), min(rt_2)), max(max(rt_1), max(rt_2)))
    rt_width = rt_range[1] - rt_range[0]
    min_axis = rt_range[0] - rt_width * expand
    max_axis = rt_range[1] + rt_width * expand
    ax.set_xlim(min_axis, max_axis)
    ax.set_ylim(min_axis, max_axis)
    ax.set_aspect("equal")
    if rt_unit:
        unit_suffix = f" ({rt_unit})"
    else:
        unit_suffix = ""
    ax.set_xlabel(f"{x_label}{unit_suffix}")
    ax.set_ylabel(f"{y_label}{unit_suffix}")
    return min_axis, max_axis


def ex_line_dict(obse_rt, pred_rt, ex_line):
    ex_dict = dict()
    ex_line = sorted(list(ex_line), reverse=True)
    for _each_ex in ex_line:
        _each_ex = _each_ex * 100 if _each_ex <= 1 else _each_ex
        ex_dict[str(_each_ex)] = delta_tx_to_rt_2diff(obse_rt, pred_rt, _each_ex)
    return ex_dict


def rt_reg(
    obse_rt,
    pred_rt,
    ex_line=(95, 85, 75),
    ex_line_num=1,
    ex_linewidth=1.0,
    diagonal=True,
    diagonal_linewidth=1.0,
    scatter_size=1.5,
    scatter_color="#5250AD",
    rt_unit="units",  # rt_units -> label_suffix
    delta_metric_name="t",
    delta_metric_dotf=3,
    delta_metric_multi_by=1,
    anno_fontsize=10,
    anno_gap=12.5,
    anno_group_row_gap: int = 1,  # anno text, unit of anno number
    # PCC:True/False, R2:True/False, n:True/False, combine these params to a dict and the order is defined as the key order in dict
    # How to add other params    active=False -> Return the class and need to run .active_anno() method
    x_label="Observed RT",
    y_label="Predicted RT",
    title="RT correlation",
    scat_label=None,
    ax=None,
    save=None,
):
    if ax is None:
        ax = plt.gca()
    min_axis, max_axis = define_reg_ax(ax, obse_rt, pred_rt, x_label, y_label, rt_unit)

    if ex_line:
        ex_dict = ex_line_dict(obse_rt, pred_rt, ex_line)
    else:
        ex_dict = None

    ax.set_title(title)

    scat = ax.scatter(obse_rt, pred_rt, c=scatter_color, s=scatter_size, label=scat_label)

    if diagonal:
        ax.plot([min_axis, max_axis], [min_axis, max_axis], color="k", linewidth=diagonal_linewidth)

    delta_metric_multi_by_anno = f" * {delta_metric_multi_by}" if (delta_metric_multi_by != 1) else ""
    annotate_text_ex = []
    if ex_dict:
        for _i, (_ex_num, _ex_value) in enumerate(ex_dict.items()):
            try:
                _color = S[_i]
            except IndexError:
                _color = "k"
            if _i < ex_line_num:
                ax.plot(
                    [min_axis, max_axis],
                    [min_axis - _ex_value / 2, max_axis - _ex_value / 2],
                    color=_color,
                    linewidth=ex_linewidth,
                )
                ax.plot(
                    [min_axis, max_axis],
                    [min_axis + _ex_value / 2, max_axis + _ex_value / 2],
                    color=_color,
                    linewidth=ex_linewidth,
                )
            annotate_text_ex.append(
                rf"$\Delta${delta_metric_name}$_{{{_ex_num}\%}}$ = {_ex_value * delta_metric_multi_by:.3f} ({rt_unit}{delta_metric_multi_by_anno})"
            )

    p = pearsonr(obse_rt, pred_rt)
    r_2 = r_square(obse_rt, pred_rt)

    annotate_text_info = [f"PCC: {p[0]:.4f}", f"R$^2$: {r_2:.4f}", f'n={format(len(obse_rt), ",")}']

    annotation = annotate_text_ex + [""] * anno_group_row_gap + annotate_text_info
    for _i, _anno in enumerate(annotation):
        _ = ax.annotate(
            _anno,
            xy=(min_axis, max_axis),
            fontsize=anno_fontsize,
            va="top",
            ha="left",
            textcoords="offset points",
            xytext=(5, -anno_gap * (_i + 0.5)),
        )

    if save:
        plt.savefig(save + ".RT.png")

    return scat, annotate_text_ex, annotate_text_info
