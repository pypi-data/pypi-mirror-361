import numpy as np
import pandas as pd
import scipy.stats
from matplotlib import pyplot as plt

from mskit.plot_kit.annotations import bar_anno, dyna_bar_anno
from mskit.plot_kit.colors import PreColorDict
from mskit.plot_kit.drawing_area import ax_utls
from mskit.plot_kit.drawing_area import remove_target_spines
from mskit.plot_kit.drawing_area import set_thousand_separate


def get_exp_ratio_idx(data: pd.Series, exp_ratio):
    data = data.cumsum() / data.sum()
    exp_ident = []
    for ratio in exp_ratio:
        ident = data[data > ratio].index[0]
        exp_ident.append(ident)
    return data, exp_ident


def cumu_bar(
    data,
    exp_ratio=(0.8, 0.9, 0.95, 0.99),
    max_ylim=5000,
    xlim=(6, 53),
    left_axis_pos=5.5,
    right_axis_pos=53.5,
    bottom_axis_pos=-8,
    mark_min_max=True,
    bar_width=0.6,
    bar_color="#CDC5BF",
    mark_bar_width=0.6,
    mark_bar_color="#8B8682",
    mark_line_style="dashed",
    cumu_line_color="#EE7600",
    vline_color="#CDC9A5",
    xlabel="Peptide length",
    ylabel="Number of stripped peptide",
    cumu_ylabel="Cumulation percent",
    title="",
    ax=None,
):
    if ax is None:
        ax = plt.gca()

    if isinstance(data, list):
        ser = pd.Series(dict(data))
    elif isinstance(data, dict):
        ser = pd.Series(data)
    elif isinstance(data, pd.Series):
        ser = data
    else:
        raise TypeError
    ser = ser.sort_index()

    ax_cumu = ax.twinx()

    remove_target_spines(["top", "right"], ax=ax)
    remove_target_spines(["top", "left", "bottom"], ax=ax_cumu)

    min_data_x, max_data_x = ser.index.min(), ser.index.max()
    min_data_y, max_data_y = ser.min(), ser.max()

    percent_cumu_ser, marked_idx = get_exp_ratio_idx(ser, exp_ratio=exp_ratio)
    cumu_num = percent_cumu_ser * max_data_y

    if max_ylim:
        ...
    else:
        ...

    for idx, num in ser.items():
        if idx in marked_idx:
            ax.bar(idx, num, width=mark_bar_width, bottom=True, color=mark_bar_color)
            ax.vlines(x=idx, ymin=num, ymax=cumu_num.loc[idx], colors=vline_color, linestyles=mark_line_style, label="")
        elif mark_min_max and idx in [min_data_x, max_data_x]:
            ax.bar(idx, num, width=mark_bar_width, bottom=True, color=mark_bar_color)
        else:
            ax.bar(idx, num, width=bar_width, bottom=True, color=bar_color)

    cumu_line = ax_cumu.plot(ser.index.tolist(), cumu_num.values, color=cumu_line_color)

    ax.set_ylim(0, max_ylim)
    ax.set_xlim(*xlim)
    ax.set_xticks([min_data_x, *marked_idx, max_data_x])
    set_thousand_separate(ax=ax, axis="y")

    cumu_ax_yscale = max_data_y
    ax_cumu.set_ylim(bottom=0, top=max_ylim, emit=True, auto=False, ymin=None, ymax=None)
    ax_cumu.set_yticks(np.arange(0, 1.1, 0.1) * cumu_ax_yscale)
    ax_cumu.set_yticklabels(["{}%".format(_) for _ in range(0, 101, 10)])

    ax.spines["left"].set_position(("data", left_axis_pos))
    ax.spines["bottom"].set_position(("data", bottom_axis_pos))
    ax_cumu.spines["right"].set_position(("data", right_axis_pos))

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax_cumu.set_ylabel(cumu_ylabel)

    ax.set_title(title)


def count_bar(
    data,
    sort_index=True,
    ylim=None,
    xlim=None,
    bar_width=0.6,
    bar_color=None,
    anno_format=",",
    anno_rotation=90,
    x_ticks=None,
    x_tick_rotation=0,
    y_tick_thousand=True,
    xlabel="Missed cleavage",
    ylabel="Number of peptides",
    title="",
    ax=None,
):
    if ax is None:
        ax = plt.gca()

    if isinstance(data, list):
        ser = pd.Series(dict(data))
    elif isinstance(data, dict):
        ser = pd.Series(data)
    elif isinstance(data, pd.Series):
        ser = data
    else:
        raise TypeError
    if sort_index:
        ser = ser.sort_index()

    data_keys, data_values = list(zip(*pd.Series(ser).items()))
    if x_ticks is not None:
        bar_xsite = x_ticks
    else:
        bar_xsite = list(range(1, len(data_keys) + 1))

    ax.bar(bar_xsite, data_values, width=bar_width, color=bar_color)
    for site, value in zip(bar_xsite, data_values):
        ax.annotate(format(value, anno_format), (site, value / 2), ha="center", rotation=anno_rotation)

    ax.set_xticks(bar_xsite)
    ax.set_xticklabels(data_keys, rotation=x_tick_rotation)

    if y_tick_thousand:
        set_thousand_separate(ax, "y")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)


def comp_bar(
    data_dict,
    base_key=None,
    comp_keys=None,
    filter_func=None,  # 对 input data dict 的每个 value 做一步 filter
    base_x_pos=1,
    bar_width=0.4,
    share_color=None,
    new_color=None,
    loss_color=None,
    bar_edge_color="grey",
    bar_edge_width=0.2,
    anno_rotation=90,
    anno_fontsize=8,
    anno_ha="center",
    anno_va="center",
    label_name=None,
    label_shift=0.1,
    ylabel="",
    title="",
    ax=None,
    save=None,
):
    if ax is None:
        ax = plt.gca()

    if share_color is None:
        share_color = PreColorDict["Blue"][75]
    if new_color is None:
        new_color = PreColorDict["Red"][60]
    if loss_color is None:
        loss_color = PreColorDict["Grey"][60]

    ax_utls.remove_xy_ticks(ax)
    ax_utls.remove_target_spines(("right", "top"), ax)
    ax_utls.set_bottom_spine_pos0(ax)

    base_data = set(data_dict[base_key])
    if filter_func:
        base_data = filter_func(base_data)
    base_len = len(base_data)
    ax.bar(
        base_x_pos, base_len, width=bar_width, bottom=0, color=share_color, lw=bar_edge_width, edgecolor=bar_edge_color
    )
    bar_anno(
        base_len,
        base_x_pos,
        y_bottom=0,
        thousand_separ=True,
        ha=anno_ha,
        va=anno_va,
        rotation=anno_rotation,
        fontsize=anno_fontsize,
        ax=ax,
    )

    for key_index, each_comp_key in enumerate(comp_keys):
        bar_x_pos = key_index + base_x_pos + 1
        comp_data = set(data_dict[each_comp_key])
        if filter_func:
            comp_data = filter_func(comp_data)

        new_data_num = len(comp_data - base_data)
        share_data_num = len(comp_data & base_data)
        loss_data_num = len(base_data - comp_data)

        # Share
        ax.bar(
            bar_x_pos,
            share_data_num,
            width=bar_width,
            bottom=0,
            color=share_color,
            lw=bar_edge_width,
            edgecolor=bar_edge_color,
        )
        bar_anno(
            share_data_num,
            bar_x_pos,
            y_bottom=0,
            thousand_separ=True,
            ha=anno_ha,
            va=anno_va,
            rotation=anno_rotation,
            fontsize=anno_fontsize,
            ax=ax,
        )

        # New
        ax.bar(
            bar_x_pos,
            new_data_num,
            width=bar_width,
            bottom=share_data_num,
            color=new_color,
            lw=bar_edge_width,
            edgecolor=bar_edge_color,
        )
        dyna_bar_anno(
            new_data_num,
            bar_x_pos,
            y_bottom=share_data_num,
            thousand_separ=True,
            ha=anno_ha,
            va=anno_va,
            rotation=anno_rotation,
            fontsize=anno_fontsize,
            auto_ha_va=True,
            ax=ax,
        )

        # Loss
        ax.bar(
            bar_x_pos,
            -loss_data_num,
            width=bar_width,
            bottom=0,
            color=loss_color,
            lw=bar_edge_width,
            edgecolor=bar_edge_color,
        )
        dyna_bar_anno(
            loss_data_num,
            bar_x_pos,
            y_height=-loss_data_num,
            y_bottom=0,
            thousand_separ=True,
            ha=anno_ha,
            va=anno_va,
            rotation=anno_rotation,
            fontsize=anno_fontsize,
            auto_ha_va=True,
            ax=ax,
        )

    if label_name:
        for label_index, each_name in enumerate(label_name):
            ax.annotate(
                each_name,
                (label_index + 1 + bar_width / 2 + label_shift, ax.get_ylim()[0]),
                rotation=90,
                va="bottom",
                ha="left",
                fontsize=anno_fontsize,
            )

    # ax.set_ylabel(ylabel)
    ax.set_title(title)

    if save:
        plt.savefig(save + ".Comp.png")


def hist_plot(values, bin_num=100, bin_width=None, norm=False, kde=False, kde_points=1000, ax=None):
    """
    both bin_num and bin_width will control number of bins and width of bars,
        and bin_width will have higher priority to overwrite bin_num when it's defined

    """
    if ax is None:
        ax = plt.gca()

    value_num = len(values)
    value_cover_range = np.max(values) - np.min(values)

    if bin_width is not None:
        if isinstance(bin_width, (float, int)):
            bin_num = int(np.ceil(value_cover_range / bin_width))
            bin_width = value_cover_range / bin_num
    else:
        bin_width = value_cover_range / bin_num

    df = align_sam[align_sam["Ref"] == chrom].copy()
    plt.figure(figsize=(11, 3.3))

    for idx, frag_pos in enumerate(
        [
            np.sort(df[df["IsUniqueAligned"]]["Pos"].values),
            np.sort(df[~df["IsUniqueAligned"]]["Pos"].values),
            np.sort(df["Pos"].values),
        ]
    ):
        if len(frag_pos) == 0:
            continue
        kde = scipy.stats.kde.gaussian_kde(frag_pos)
        kde_x = np.linspace(frag_pos[0], frag_pos[-1], kde_points)
        kde_y = kde(kde_x)

        bin_edges = np.linspace(np.min(frag_pos), np.max(frag_pos), bin_num)
        cumu_hist_num = np.where(
            (np.repeat(frag_pos.reshape((1, -1)), bin_num, axis=0) - bin_edges.reshape((bin_num, -1))) < 0, 1, 0
        ).sum(axis=1)
        cumu_hist_num[1:] = np.diff(cumu_hist_num)
        cumu_hist_num = cumu_hist_num / np.max(cumu_hist_num) * np.max(kde_y)

        n = format(len(frag_pos), ",")
        plt.plot(kde_x, kde_y, label="")
        plt.bar(bin_edges, cumu_hist_num, width=bin_width, alpha=0.4)

    plt.xlabel("Chrom pos")
    plt.ylabel("Density")
    plt.title(chrom)

    plt.legend(loc="upper right")
    plt.savefig(f"{chrom}.jpg", dpi=300)
