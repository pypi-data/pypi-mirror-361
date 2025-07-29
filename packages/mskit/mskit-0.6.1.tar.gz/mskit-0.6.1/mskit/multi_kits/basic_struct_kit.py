import copy
import random
from typing import Any, Union
import networkx as nx

import numpy as np
import pandas as pd


def get_directed_paths_from_pairs(*pairs):
    paths = []
    node_to_path_idx = dict()
    for pair in pairs:
        match len(pair):
            case 1:
                pass
            case 2:
                elem1, elem2 = pair
                if (node_to_path_idx.get(elem1, None)) is None:
                    paths.append(pair)
                    idx = len(paths) - 1
                    node_to_path_idx[elem1] = ([idx], [], [])
                else:
                    start, middle, end = node_to_path_idx[elem1]

                    if (len(middle) == 0) and (len(end) == 0):
                        paths.append(pair)
                        idx = len(paths) - 1
                        node_to_path_idx[elem1][0].append(idx)

                    for idx in middle:
                        raw_path = paths[idx]
                        paths.append(raw_path[: raw_path.index(elem1)] + list(pair))
                        idx = len(paths) - 1
                        node_to_path_idx[elem1][1].append(idx)

                    for idx in end:
                        paths[idx] = paths[idx] + [elem2]

                        paths.append(raw_path[: raw_path.index(elem1)] + list(pair))
                        idx = len(paths) - 1
                        node_to_path_idx[elem1][2].append(idx)
            case _:
                raise ValueError(f"Pair must have 1 or 2 elements, got {len(pair)} in {pair}")
    all_nodes = flatten_nested_list(pairs)


def get_all_paths_from_digraph(graph: nx.DiGraph):
    unique_long_paths = {}
    for source_node in graph.nodes:
        for target_node in graph.nodes:
            if source_node != target_node:
                paths = nx.all_simple_paths(graph, source=source_node, target=target_node)
                for path in paths:
                    if path[0]:
                        ...


def split_nparts(
    data: Union[list, tuple, np.ndarray],
    ratios: Union[str, list, tuple, np.ndarray],
    ratio_sep: str = ",",
    assign_remainder: str = "first_n",
    shuffle: bool = True,
    return_idx: bool = False,
    multi: bool = True,
    seed: Union[int, random.Random] = None,
) -> list:
    """
    TODO when multi datasets are passed, need to keep the choice of index same for multi datasets
    """

    if isinstance(ratios, str):
        ratios = [float(_) for _ in ratios.split(ratio_sep)]
    if len(ratios) == 1:
        return data

    n_data = len(data)
    if n_data < len(ratios):
        print()
        # or warning or raise
    ratios = np.asarray(ratios)
    split_n_data = (ratios / np.sum(ratios) * n_data).astype(int)
    if assign_remainder == "first":
        split_n_data[0] += n_data - np.sum(split_n_data)
    elif assign_remainder == "last":
        split_n_data[-1] += n_data - np.sum(split_n_data)
    elif assign_remainder == "first_n":
        split_n_data[: (n_data - np.sum(split_n_data))] += 1
    elif assign_remainder == "last_n":
        split_n_data[-(n_data - np.sum(split_n_data)) :] += 1
    elif assign_remainder == "no":
        pass
    else:
        raise ValueError("")

    cum_split_n_data = np.cumsum(split_n_data)

    if isinstance(seed, random.Random):
        r = seed
    else:
        r = random.Random(seed)

    if shuffle:
        data = copy.deepcopy(data)
        r.shuffle(data)

    split_data = [data[: cum_split_n_data[0]]]
    for idx, n in enumerate(cum_split_n_data[1:], 1):
        split_data.append(data[cum_split_n_data[idx - 1] : n])
    return split_data


def flatten_nested_list(nested_list):
    temp = []
    for _ in nested_list:
        temp.extend(_)
    return temp


flatten_list = flatten_nested_list
sum_list = flatten_nested_list


def recursive_flatten_nested_list(nested_list: list) -> list:
    """
    Recursively flatten list consist of both list/tuple and un-iterable items
    TODO append method will take much time?
        # inner_item_is_list = [isinstance(_, _) for _ in l]
        # if any(inner_item_is_list):
    """
    temp = []
    for item in nested_list:
        if isinstance(item, (list, tuple)):
            temp.extend(recursive_sum_list(item))
        else:
            temp.append(item)
    return temp


recursive_sum_list = recursive_flatten_nested_list


def drop_list_duplicates(initial_list: list) -> list:
    return sorted(list(set(initial_list)), key=initial_list.index)


def intersect_lists(*lists, drop_duplicates=True):
    temp = lists[0]
    if drop_duplicates:
        temp = drop_list_duplicates(temp)
    for l in lists[1:]:
        temp = [_ for _ in temp if _ in l]
    return temp


def subtract_list(list_1, list_2, drop_duplicates=True):
    subtracted_list = [_ for _ in list_1 if _ not in list_2]
    if drop_duplicates:
        return drop_list_duplicates(subtracted_list)
    else:
        return subtracted_list


def union_dicts(*dicts: dict, init=None, copy_init=True, iter_depth=-1):
    if init is None:
        temp = {}
    else:
        temp = copy.deepcopy(init) if copy_init else init
    for d in dicts:
        temp.update(d)
    return temp


def update_dict_recursively(acceptor: dict, donor: dict, copy: bool = True):
    if copy:
        acceptor = copy.deepcopy(acceptor)
    for k, v in donor.items():
        if isinstance(v, dict):
            acceptor[k] = update_dict_recursively(acceptor.get(k, {}), v)
        else:
            acceptor[k] = v
    return acceptor


def intersect_dict(*dicts) -> dict:
    shared_keys = intersect_sets(*dicts)
    return {k: v for k, v in dicts[0].items() if k in shared_keys}


def align_dicts(
    *dn: dict,
    d_names=None,
    assign_to_empty: Any = np.nan,
    key_order: str = "union_sort",
):
    """
    union_sort
    indict_order
    indict_order_sort
    """
    if isinstance(key_order, str):
        if key_order == "union_sort":
            keys = sorted(set(sum_list(dn)))
        elif ...:
            ...
        else:
            raise ValueError(f"unknown `key_order`: {key_order}")
    elif isinstance(key_order, (list, tuple)):
        keys = key_order
    else:
        raise ValueError(f"unknown `key_order` type: {type(key_order)}")

    aligned = []
    for key in keys:
        aligned.append([di.get(key, assign_to_empty) for di in dn])
    if d_names is None:
        d_names = [f"D{i}" for i in range(1, len(dn) + 1)]
    return pd.DataFrame(aligned, index=keys, columns=d_names)


def align_dict_values(
    d: dict[Any, list[str]], sort_keys: bool = True, sort_values: bool = False, based_on_key: str = None
) -> pd.DataFrame:
    """
    Construct a dataframe with dict keys as columns and dict values (list of strings) as rows.
    The values are True if the string is in the list of the corresponding key, otherwise False.

    Parameters
    ----------
    d : dict
        Dictionary with keys as group names and values as list of string items.
    """
    all_keys = list(d.keys())
    if sort_keys:
        all_keys = sorted(all_keys)
    based_on_key = based_on_key or all_keys[0]
    if sort_values:
        d[based_on_key] = sorted(d[based_on_key])
    all_values = d[based_on_key]
    for key in [k for k in all_keys if k != based_on_key]:
        all_values += [v for v in d[key] if v not in all_values]
    df = pd.DataFrame([[(v in d[k]) for k in all_keys] for v in all_values], index=all_values, columns=all_keys)
    return df


def print_better_dict(d):
    for k, v in d.items():
        print(f"'{k}': [")
        for _v in v:
            print(f"    '{_v}',")
        print(f"],")


def union_sets(*sets):
    _set = sets[0]
    for s in sets[1:]:
        _set = _set | s
    return _set


def intersect_sets(*sets, iter_depth=-1):
    _set = sets[0]
    for s in sets[1:]:
        _set = _set & s
    return _set


def split_two_set(set1, set2):
    overlapped = set1 & set2
    set1_unique = set1 - set2
    set2_unique = set2 - set1
    return set1_unique, set2_unique, overlapped


def check_value_len_of_dict(
    checked_dict: dict,
    thousands_separator=True,
    sort_keys=False,
):
    # TODO sort_keys 可以为 lambda 函数
    # TODO return length dict or print
    if sort_keys:
        keys = sorted(checked_dict.keys())
    else:
        keys = checked_dict.keys()
    for k in keys:
        v = checked_dict[k]
        v_len = len(v)
        if thousands_separator:
            print(f'{k}: {format(v_len, ",")}')
        else:
            print(f"{k}: {v_len}")


class NonOverwriteDict(dict):
    def __setitem__(self, key, value):
        if self.__contains__(key):
            pass
        else:
            dict.__setitem__(self, key, value)


class XmlListConfig(list):
    def __init__(self, x_list):
        super(XmlListConfig, self).__init__()
        for element in x_list:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    def __init__(self, parent_element):
        super(XmlDictConfig, self).__init__()
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    x_dict = XmlDictConfig(element)
                else:
                    x_dict = {element[0].tag: XmlListConfig(element)}
                if element.items():
                    x_dict.update(dict(element.items()))
                self.update({element.tag: x_dict})
            elif element.items():
                self.update({element.tag: dict(element.items())})
            else:
                self.update({element.tag: element.text})


def xml_to_dict(xml_context):
    from xml.etree import cElementTree as ElementTree

    _root = ElementTree.XML(xml_context)
    _xml_dict = XmlDictConfig(_root)
    return _xml_dict
