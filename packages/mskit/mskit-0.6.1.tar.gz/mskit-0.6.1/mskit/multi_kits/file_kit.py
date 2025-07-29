import io
import os
from pathlib import Path
import glob
import pickle
import shutil
import time
import typing
import csv
import concurrent.futures
from typing import Optional, Iterable
import subprocess
import platform

from tqdm import tqdm

import numpy as np
import pandas as pd

from .basic_struct_kit import sum_list


def count_lines(filepath):
    """
    Count the number of lines in a file.

    Parameters
    ----------
    filepath : str
        The path to the file.

    Returns
    -------
    int
        The number of lines in the file.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    PermissionError
        If the user does not have permission to read the file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")

    if not os.access(filepath, os.R_OK):
        raise PermissionError(f"You don't have permission to read '{filepath}'.")

    try:
        if platform.system() in ["Linux", "Darwin"]:  # Linux or macOS
            # Use wc command for UNIX-like systems
            result = subprocess.run(["wc", "-l", filepath], capture_output=True, text=True, check=True)
            return int(result.stdout.split()[0])
        else:
            # Fallback to Python method for other systems
            return count_file_lines(filepath)
    except subprocess.CalledProcessError:
        # If wc command fails, fallback to Python method
        return count_file_lines(filepath)
    except ValueError:
        # If parsing the wc output fails, fallback to Python method
        return count_file_lines(filepath)


def count_file_lines(filepath):
    """
    fallback of count lines.
    """
    with open(filepath, "rb") as file:
        return sum(bl.count(b"\n") for bl in iter(lambda: file.read(8192), b""))


def concat_files(
    file_list: Optional[Iterable[str]] = None,
    glob_pattern: Optional[str] = None,
    output_file: str = "combined.txt",
    show_progress: bool = True,
):
    """
    Concatenates the contents of multiple files into a single output file.

    Args:
        file_list (Optional[Iterable[str]]): A list of file paths to be concatenated. If not provided, `glob_pattern` will be used to find files.
        glob_pattern (Optional[str]): A glob pattern to match files to be concatenated. If `file_list` is provided, this argument will be ignored.
        output_file (str): The path of the output file where the concatenated contents will be written. Default is 'combined.txt'.
        show_progress (bool): Whether to show progress bar while concatenating files. Default is True.

    Raises:
        ValueError: If neither `file_list` nor `glob_pattern` is provided, or if both are provided.

    """
    if file_list is None:
        if glob_pattern is None:
            raise ValueError("Must provide file_list or glob_pattern")
        else:
            file_list = glob.glob(glob_pattern)
    else:
        if glob_pattern is not None:
            raise ValueError("Can not provide both file_list and glob_pattern")

    if show_progress:
        file_list = tqdm(file_list)

    with open(output_file, "w") as f:
        for file in file_list:
            with open(file, "r") as f2:
                f.write(f2.read())


def add_anno_to_path_ahead_suffix(fp, anno):
    """
    Add an annotation to the path ahead of the file suffix.

    Args:
        fp (str): The file path.
        anno (str): The annotation to add.

    Returns:
        str: The modified file path with the annotation added.
    """
    return os.path.join(
        os.path.dirname(fp),
        "".join([f"{t}-{anno}" if (i == 0) else t for i, t in enumerate(os.path.splitext(os.path.basename(fp)))]),
    )


def read_file_before_n_symbol(
    filepath: os.PathLike,
    symbol: str = "\n",
    n: int = 1,
    openmode: str = "r",
    encoding: str = "utf-8",
):
    _c = 0
    with open(filepath, openmode, encoding=encoding) as f:
        while True:
            char = f.read(1)
            if char == symbol:
                _c += 1
            if _c == n:
                break
        end_pos = f.tell()
        f.seek(0)
        return f.read(end_pos - n)


def read_csv_chunk(file_path, start_rowidx, end_rowidx, delimiter="\t"):
    """
    Read a chunk of a CSV file.

    Args:
        file_path (str): The path to the CSV file.
        start_rowidx (int): The starting row index.
        end_rowidx (int): The ending row index.
        delimiter (str, optional): The delimiter used in the CSV file. Defaults to '\t'.

    Returns:
        list: The data read from the chunk of the CSV file.
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=delimiter)
        for i, row in enumerate(reader):
            if i < start_rowidx:
                continue
            if i > end_rowidx:
                break
            data.append(row)
    return data


def read_csv_parallel(file_path, num_partitions, delimiter="\t"):
    """
    Read a CSV file in parallel by dividing it into multiple partitions.

    Args:
        file_path (str): The path to the CSV file.
        num_partitions (int): The number of partitions to divide the file into.
        delimiter (str, optional): The delimiter used in the CSV file. Defaults to '\t'.

    Returns:
        list: A list of results from each partition.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        # Count the total number of rows in the CSV file
        total_rows = sum(1 for _ in csv.reader(file, delimiter=delimiter))

    chunk_size = total_rows // num_partitions
    partitions = [(i * chunk_size, (i + 1) * chunk_size - 1) for i in range(num_partitions - 1)]
    partitions.append(((num_partitions - 1) * chunk_size, total_rows - 1))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(read_csv_chunk, file_path, start, end) for start, end in partitions]

        # Wait for all tasks to complete and gather the results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    return results


def split_file_nparts(
    filepath: os.PathLike,
    output_folder: os.PathLike = None,
    expected_nparts: int = 10,
    required_part_idx: tuple = None,
    start_pos: int = 0,
    openmode: str = "r",
    writemode: str = "w",
    identifier_pos: str = "before_suffix",
):
    dir_name = os.path.dirname(filepath)
    basename, suffix = os.path.splitext(os.path.basename(filepath))
    if output_folder is None:
        output_folder = dir_name
    else:
        os.makedirs(output_folder, exist_ok=True)
    with open(filepath, openmode) as f:
        size = f.seek(0, 2)
        part_size = int(np.ceil(size / expected_nparts))
        curr_pos = start_pos
        f.seek(curr_pos)
        for idx, end in enumerate([*list(range(part_size, size, part_size)), size], 1):
            if required_part_idx is not None and idx not in required_part_idx:
                continue
            if identifier_pos == "before_suffix":
                new_file = os.path.join(dir_name, f"{basename}-Part{idx}_{end}.{suffix}")
            elif identifier_pos == "after_file":
                new_file = f"{filepath}-Part{idx}_{end}"
            else:
                raise ValueError
            with open(new_file, writemode) as f2:
                while curr_pos <= end:
                    f2.write(f.readline())
                    curr_pos = f.tell()


def adjust_file_block_pos(
    f: io.TextIOWrapper, start_pos: int, end_pos: int, split_symbol: str = "\n", adjust_direct: str = "forward"
):
    """
    adjust_direct: 'forward' or 'backward'

    """
    # TODO
    if start_pos != 0:
        f.seek(start_pos - 1)
        if f.read(1) != "\n":
            line = f.readline()
            start_pos = f.tell()
    f.seek(start_pos)
    while start_pos <= end_pos:
        line = f.readline()
        start_pos = f.tell()


def split_file_block(
    file: typing.Union[str, io.TextIOWrapper],
    mode="rb",
    block_num: int = None,
    block_adjust_symbol=None,
):
    if block_num is None:
        block_num = os.cpu_count()
    if isinstance(file, io.TextIOWrapper):
        file = file.name

    with open(file, mode) as f:
        file_size = f.seek(0, 2)
        if file_size < block_num:
            raise ValueError(f"Input file size is smaller than block number: {block_num} blocks for file {file}")
        block_size = int(file_size / block_num)

        # TODO check \n or other defined symbol in loop and adjust position
        #  `If block_adjust_symbol is not None: adjust_file_block_pos...`
        pos_list = []
        start_pos = 0
        for i in range(block_num):
            if i == block_num - 1:
                end_pos = file_size - 1
                pos_list.append((start_pos, end_pos))
                break
            end_pos = start_pos + block_size - 1
            if end_pos >= file_size:
                end_pos = file_size - 1
            if start_pos >= file_size:
                break
            pos_list.append((start_pos, end_pos))
            start_pos = end_pos + 1

    return pos_list


def recursive_copy(original, target, ignored_items=None, verbose=True, exist_ok=True):
    if ignored_items is None:
        ignored_items = []

    os.makedirs(target, exist_ok=exist_ok)
    curr_items = os.listdir(original)
    for item in curr_items:
        if item in ignored_items:
            continue
        original_item_path = os.path.join(original, item)
        target_item_path = os.path.join(target, item)
        if os.path.isdir(original_item_path):
            recursive_copy(original_item_path, target_item_path, ignored_items=ignored_items, verbose=verbose)
        elif os.path.isfile(original_item_path):
            if verbose:
                print(f"copying {item} from {original_item_path} to {target_item_path}")
            shutil.copy(original_item_path, target_item_path)
        else:
            raise
    return 0


def get_workspace(level=0):
    curr_dir = os.path.abspath(".")
    work_dir = curr_dir
    for i in range(level):
        work_dir = os.path.dirname(work_dir)
    return work_dir


def list_dir_with_identification(dirname, identification=None, position="end", regex=False, full_path=False):
    dir_content_list = os.listdir(dirname)
    if identification:
        if position == "end":
            dir_content_list = [_ for _ in dir_content_list if _.endswith(identification)]
        elif position == "in":
            dir_content_list = [_ for _ in dir_content_list if identification in _]
        else:
            raise NameError("parameter position is illegal")
    if not full_path:
        return dir_content_list
    else:
        return [os.path.join(dirname, _) for _ in dir_content_list]


def file_prefix_time(with_dash=False):
    curr_time = time.strftime("%Y%m%d", time.localtime())
    prefix = curr_time + "-" if with_dash else curr_time
    return prefix


def pd_read_csv_skip_row(file, comment=None, file_mode="r", file_encode="utf8", **pd_kwargs):
    if os.stat(file).st_size == 0:
        raise ValueError("File is empty")
    with open(file, file_mode, encoding=file_encode) as f_handle:
        pos = 0
        cur_line = f_handle.readline()
        while cur_line.startswith(comment):
            pos = f_handle.tell()
            cur_line = f_handle.readline()
            f_handle.seek(pos)
    return pd.read_csv(f_handle, **pd_kwargs)


def read_one_col_file(file_path, skiprows=None, file_mode="r", file_encode="utf8"):
    with open(file_path, file_mode, encoding=file_encode) as f_handle:
        one_col_list = [row.strip("\n") for row in f_handle.readlines()]
        one_col_list = one_col_list[skiprows:] if skiprows is not None else one_col_list
        while "" in one_col_list:
            one_col_list.remove("")
    return one_col_list


def write_to_one_col_file(data, file_path, header=None, file_mode="w", file_encode="utf8"):
    with open(file_path, file_mode, encoding=file_encode) as f:
        if header is not None:
            f.write(header + "\n")
        for one in data:
            f.write(one + "\n")
    return file_path


def flatten_two_headers_file(file, header_num=2, sep=",", method=None) -> pd.DataFrame:
    """
    :param file: path of file, or file text in string format, or list of lines
    :param header_num:
    :param sep:
    :param method:

    method: stack headers or cross-insert or lower-first

    Headle file with two headers like

    Peptide_Order	Peptide	Peptide_Mass	Modifications	Proteins
        Spectrum_Order	Title	Charge	Precursor_Mass
    1	AAAAAAAAAAAAAAAAAA	2000	Carbamidomethyl[C](9)	PAK
        1	T1	3	1999
        2	T2	3	1999
        3	T3	3	1999
        4	T1	3	1999
        5	T5	3	1999
    2	CCCCCCCCCCCCCCC	3000	Carbamidomethyl[C](15)	PBK
        1	T2	3	2999
    3	DDDDDDDDDDDDDDDD	4000	null	PCK
        1	T3	3	3999
        2	T1	3	3999
        3	T2	3	3999

    """
    if isinstance(file, str):
        if len(file) < 500 and os.path.exists(file):
            with open(file, "r") as f:
                file = f.readlines()
        else:
            file = file.split("\n")

    headers = [file[i].rstrip(f"\n{sep}").split(sep) for i in range(header_num)]
    headers_used_col_idx = [[idx for idx, value in enumerate(header) if value != ""] for header in headers]
    headers_used_col_num = [len(idx) for idx in headers_used_col_idx]

    if method is None or method == "stack":
        flatten_text_used_col_idx = []
        for idx, num in enumerate([0, *headers_used_col_num][:-1]):
            flatten_text_used_col_idx.append(np.arange(num, num + headers_used_col_num[idx]))
    elif method == "cross-insert":
        flatten_text_used_col_idx = []
    elif method == "lower-first":
        flatten_text_used_col_idx = []
    else:
        raise

    flatten_header = sum_list([[value for value in header if value != ""] for header in headers])
    flatten_col_num = len(flatten_header)
    flatten_text = []

    header_level = 1
    consensus_text = ["" for i in range(flatten_col_num)]
    for row in file[header_num:]:
        row = row.rstrip(f"\n{sep}").split(sep)
        for idx, value in enumerate(row, 1):
            if value != "":
                header_level = idx
                break
        if header_level == 1:
            consensus_text = ["" for i in range(flatten_col_num)]

        for value_idx, raw_idx in enumerate(headers_used_col_idx[header_level - 1]):
            consensus_text[flatten_text_used_col_idx[header_level - 1][value_idx]] = row[raw_idx]

        if header_level == header_num:
            flatten_text.append(consensus_text.copy())

    return pd.DataFrame(flatten_text, columns=flatten_header)


def process_list_or_file(x):
    if isinstance(x, list) or isinstance(x, set):
        target_list = x
    else:
        if os.path.isfile(x):
            target_list = read_one_col_file(x)
        else:
            raise
    return target_list


def print_path_basename_in_dict(path_dict: dict):
    for name, path in path_dict.items():
        print(f"{name}: {os.path.basename(path)}")


def print_path_exist():
    try:
        print(check_path)
    except FileNotFoundError:
        ...


def check_path(
    path: str | Path,
    name: str = None,
    shown_path_right_idx: typing.Union[None, int, list, tuple] = 1,
    show_all_after_idx: bool = True,
    raise_error: bool = False,
    verbose: bool = False,
):
    # TODO this file, or this dir
    path = Path(path).resolve() if isinstance(path, str) else path
    if shown_path_right_idx is None:
        shown_filepath = str(path)
    elif isinstance(shown_path_right_idx, int):
        if shown_path_right_idx < 0:
            shown_filepath = str(path)
        elif shown_path_right_idx == 0:
            shown_filepath = path.name
        else:
            shown_filepath = (
                os.path.sep.join(path.parts[-shown_path_right_idx:])
                if show_all_after_idx
                else path.parts[-shown_path_right_idx]
            )
    elif isinstance(shown_path_right_idx, (list, tuple)):
        # TODO join selected idx
        for idx in shown_path_right_idx:
            pass
    else:
        raise ValueError(
            f"Param `shown_path_right_idx` must be None or integer or list/tuple of integet. Now {shown_path_right_idx}"
        )
    if name is not None:
        print(f"{os.path.exists(path)} - {name}: {shown_filepath}")
    else:
        print(f"{os.path.exists(path)} - {shown_filepath}")


def check_path_in_dict(path_dict: dict[str, str | Path], shown_filename_right_idx: int = 1):
    # TODO 显示的文件名称可以是多个 idx 对应 substring 的组合
    """
    :param path_dict:
    :param shown_filename_right_idx: None or int. None: use full path (raw value in dict). int: use idx part of file path (right count with 1st-first idx)
    """
    print(f"Total {len(path_dict)} files")
    for name, path in path_dict.items():
        check_path(
            path=path,
            name=name,
            shown_path_right_idx=shown_filename_right_idx,
            show_all_after_idx=True,
            raise_error=False,
            verbose=False,
        )


def check_input_df(data, *args) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        if os.path.exists(data):
            df = pd.read_csv(data, *args)
        else:
            raise FileNotFoundError
    return df


def fill_path_dict(path_to_fill: str, fill_string: dict, exist_path_dict: dict = None, max_fill_padding=None):
    # TODO checking
    if exist_path_dict is None:
        path_dict = dict()
    else:
        path_dict = exist_path_dict.copy()

    if max_fill_padding is not None:
        explicit_fill_num = path_to_fill.count("{}")

    for k, file_name in fill_string.items():
        file_name = [file_name] if isinstance(file_name, str) else file_name
        path_dict[k] = path_to_fill.format(*file_name)
    return path_dict


def join_path(path, *paths, create=False):
    pass


def write_inten_to_json(prec_inten: dict, file_path):
    total_prec = len(prec_inten)
    with open(file_path, "w") as f:
        f.write("{\n")

        for prec_idx, (prec, inten_dict) in enumerate(prec_inten.items(), 1):
            f.write('    "%s": {\n' % prec)
            frag_num = len(inten_dict)
            for frag_idx, (frag, i) in enumerate(inten_dict.items(), 1):
                if frag_idx != frag_num:
                    f.write(f'        "{frag}": {i},\n')
                else:
                    f.write(f'        "{frag}": {i}\n')

            if prec_idx != total_prec:
                f.write("    },\n")
            else:
                f.write("    }\n")

        f.write("}")


def data_dump_load_skip(file_path, data=None, cover_data=False, update_file=False):
    if not os.path.exists(file_path):
        # Here use 'is not None' because some thing will be wrong when the data is a pd.DataFrame. (Truth value is ambiguous error)
        if data is not None:
            with open(file_path, "wb") as f:
                pickle.dump(data, f)
        else:
            raise FileNotFoundError("No existing file and no input data")
    else:
        if data is not None:
            if update_file:
                with open(file_path, "wb") as f:
                    pickle.dump(data, f)
            elif cover_data:
                with open(file_path, "rb") as f:
                    data = pickle.load(f)
            else:
                pass
        else:
            with open(file_path, "rb") as f:
                data = pickle.load(f)
    return data


def xlsx_sheets_to_text_files(
    xlsx_path,
    output_folder,
    sheet_name_trans_func=lambda x: x.replace(" ", "_"),
    skipped_row_idx=None,
):
    try:
        import openpyxl
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Need module `openpyxl` to parse xlsx file and sheets")

    wb = openpyxl.open(xlsx_path)
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        used_name = sheet_name_trans_func(sheet_name)
        with open(os.path.join(output_folder, f"{used_name}.txt"), "w") as f:
            for row_idx, row in enumerate(sheet.iter_rows(values_only=True)):
                if isinstance(skipped_row_idx, (tuple, list)):
                    if row_idx in skipped_row_idx:
                        continue
                row = "\t".join([(str(_) if _ is not None else "") for _ in row])
                f.write(row + "\n")
