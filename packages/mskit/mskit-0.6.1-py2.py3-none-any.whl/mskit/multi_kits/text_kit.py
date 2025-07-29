import random
import re
import string
import typing

from .basic_struct_kit import sum_list


def get_random_string(
    symbols: typing.Union[list, tuple] = string.ascii_letters,
    prefix: str = "",
    suffix: str = "",
    length: int = 16,
    exclude: typing.Union[list, tuple, str, None] = None,
    seed=None,
):
    if isinstance(seed, random.Random):
        r = seed
    else:
        r = random.Random(seed)
    rand_s_length = length - len(prefix) - len(suffix)
    s = f'{prefix}{"".join(r.choices(symbols, k=rand_s_length))}{suffix}'
    if exclude is not None and s in exclude:
        s = get_random_string(symbols=symbols, prefix=prefix, suffix=suffix, length=length, exclude=exclude, seed=r)
    return s


def split_str_with_symbol_included_substring(
    s: str,
    split_symbol: str = "\t",
    special_symbol: str = '"',
    keep_spcial_symbol: bool = False,
    strip_slash_n: bool = False,
):
    if strip_slash_n:
        s = s.strip("\n")
    split_str = []
    symbol_start = False
    substr = ""
    for c in s:
        if c == special_symbol:
            symbol_start = [True, False][symbol_start]
            if keep_spcial_symbol:
                substr += c
        elif c == split_symbol:
            if symbol_start:
                substr += c
            else:
                split_str.append(substr)
                substr = ""
        else:
            substr += c
    split_str.append(substr)
    return split_str


def get_para_sep(
    name,
    fillin_symbol: str = "-",
    symbol_num: typing.Union[int, list[int]] = 15,
    space_around_name: typing.Union[int, list[int]] = 1,
) -> str:
    if isinstance(symbol_num, int):
        symbol_num = (symbol_num, symbol_num)
    if isinstance(space_around_name, int):
        space_around_name = (space_around_name, space_around_name)
    prefix = fillin_symbol * symbol_num[0] + " " * space_around_name[0] if symbol_num[0] != 0 else ""
    suffix = " " * space_around_name[1] + fillin_symbol * symbol_num[1] if symbol_num[1] != 0 else ""
    return f"{prefix}{name}{suffix}"


def get_title2idx_dict(title_content: str) -> dict:
    title_dict = dict([(__, _) for _, __ in enumerate(title_content.strip("\n").split("\t"))])
    return title_dict


def combine_delimited_text(*sn: str, delimiter: str = ";", keep_order: bool = False) -> str:
    """
    This will combine two strings with semicolons and drop duplication
    Example: s1='Q1;Q2', s2='Q2;Q3' -> 'Q1;Q2;Q3'
    Note that the order may change if keep_order=False
    """
    s_list = map(lambda _: _.strip(delimiter).split(delimiter), sn)
    flatten_s = list(filter(lambda x: True if x else False, sum(s_list, [])))
    unique_s = list(set(flatten_s))
    if keep_order:
        unique_s = sorted(unique_s, key=flatten_s.index)
    return ";".join(unique_s)


def find_char_pos_on_str(
    s: str,
    found_char: typing.Union[str, set, tuple, list],
):
    if isinstance(found_char, str):
        found_char = [found_char]
    result = []
    for i, c in enumerate(s, 1):
        if c in found_char:
            result.append(i)
    return result


def find_substring(
    s: str,
    start_char: str = "[",
    end_char: str = "]",
    keep_start_end_char: bool = True,
    substring_trans_dict: dict = None,
):
    """
    This function will find the substrings start with param "start" and end with param "end" in input "string"

    Parameters
    ----------
    s : str
        _description_
    start_char : str, optional
        _description_, by default '['
    end_char : str, optional
        _description_, by default ']'
    keep_start_end_char : bool, optional
        _description_, by default True
    substring_trans_dict : dict, optional
        _description_, by default None

    Returns
    -------
    a tuple with 3 elements
    1-th element: str
        extracted new string with no substrings
    2-nd element: list
        positions of substrings (1-indexed positions)
    3-rd element: list
        extracted substrings

    Examples
    --------
    find_substring('[Acetyl (N-term)]M[Oxidation (M)][Acetyl]VQISPDS[Phospho (STY)]GGLPER[+n][+m]', '[', ']', keep_start_end_char=False)
        ('MVQISPDSGGLPER',
            [0, 1, 1, 8, 14, 14],
            ['Acetyl (N-term)', 'Oxidation (M)', 'Acetyl', 'Phospho (STY)', '+n', '+m'])
    find_substring('AM(ox)M(Oxidation (M))C(Carbamidomethyl (C))DEEHC(Carb)K', '(', ')')
        ('AMMCDEEHCK',
        [2, 3, 4, 9],
        ['(ox)', '(Oxidation (M))', '(Carbamidomethyl (C))', '(Carb)'])
    find_substring('AM[ox]M[Oxidation (M)]C[Carbamidomethyl (C)]DEEHC[Carb]K', '[', ']')
        ('AMMCDEEHCK',
        [2, 3, 4, 9],
        ['[ox]', '[Oxidation (M)]', '[Carbamidomethyl (C)]', '[Carb]'])

    Others
    ------
    TODO 再返回一个对应位点氨基酸的 list  注意 N 和 C 端
    TODO substring_trans_dict
    """

    start_num = 0
    end_num = 0
    substrings = []
    pos = []
    substring_start = False
    sub_total_len = 0
    main_str = ""
    sub_str = ""
    for i, char in enumerate(s):
        if char == start_char:
            if keep_start_end_char:
                sub_str += char
            substring_start = True
            start_num += 1
        elif char == end_char:
            if keep_start_end_char:
                sub_str += char
            end_num += 1
            if start_num == end_num:
                substrings.append(sub_str)
                sub_total_len += len(sub_str)
                if not keep_start_end_char:
                    sub_total_len += 2
                pos.append(i - sub_total_len + 1)
                start_num = 0
                end_num = 0
                sub_str = ""
                substring_start = False
        else:
            if substring_start:
                sub_str += char
            else:
                main_str += char
    return main_str, pos, substrings


substring_finder = find_substring


def check_mod_on_peps(df, col="UniModPep"):
    print(
        f'\tString included in () of "{col}":',
        sorted(set(sum_list([find_substring(_, "(", ")")[2] for _ in list(set(df[col]))]))),
    )
    print(
        f'\tString included in [] of "{col}":',
        sorted(set(sum_list([find_substring(_, "[", "]")[2] for _ in list(set(df[col]))]))),
    )


def fillin_annotation(
    s, anno_pos, anno_text, existed_anno_start_char: str = None, existed_anno_end_char: str = None
) -> str:
    """
    TODO param target_pos_char = None, check if char on target pos is expected
    TODO an error when existed_anno_start_char ~~existed on pos 0~~ existed anywhere

    :param s:
    :param anno_pos:
    :param anno_text:
    :param existed_anno_start_char:
    :param existed_anno_end_char:

    :return:

    s = 'AYHPAYTETMSMGGGSSHGGGQQYVPFATSSGSLR'
    # len(s) = 35
    fillin_annotation(
        s,
        (0, 10, 12, 34, 35, 35),
        [f'({_})' for _ in ['Acetyl', 'Oxidation', 'Oxidation', '34', '35', '35-2']],
        existed_anno_start_char='(',
        existed_anno_end_char=')'
    )
    -> '(Acetyl)AYHPAYTETM(Oxidation)SM(Oxidation)GGGSSHGGGQQYVPFATSSGSL(34)R(35)(35-2)'
    """
    if not anno_pos and not anno_text:
        return s

    if isinstance(anno_pos, (str, int)):
        anno_pos = [int(anno_pos)]
    if isinstance(anno_text, str):
        anno_text = [anno_text]

    if existed_anno_start_char is not None and existed_anno_end_char is not None:
        s, exist_anno_pos, exist_anno_text = find_substring(
            s, start_char=existed_anno_start_char, end_char=existed_anno_end_char
        )
    elif existed_anno_start_char is None and existed_anno_end_char is None:
        exist_anno_pos, exist_anno_text = [], []
    else:
        raise ValueError(
            "Both `existed_anno_start_char` and `existed_anno_end_char` need to be passed or set to None as default. "
            f"Now {existed_anno_start_char} and {existed_anno_end_char}"
        )

    exist_anno_pos += anno_pos
    exist_anno_text += anno_text

    t = sorted([(i, v) for i, v in enumerate(exist_anno_pos)], key=lambda x: x[1])
    anno_pos = [_[1] for _ in t]
    anno_text = [anno_text[i] for i in [_[0] for _ in t]]
    anno_s = ""
    _ = 0
    for pos_idx, pos in enumerate(anno_pos):
        anno_s += s[_:pos]
        anno_s += anno_text[pos_idx]
        _ = pos
    anno_s += s[pos:]
    return anno_s


def extract_bracket(
    str_with_bracket,
):  # Need a parameter to choose to use () or [] or others (by manurally define?) and a parameter to skip how many additional brackets
    bracket_start = [
        left_bracket.start() for left_bracket in re.finditer(r"\(", str_with_bracket)
    ]  # Add [::2] if there is one additional bracket in the expected one
    bracket_end = [
        right_bracket.start() for right_bracket in re.finditer(r"\)", str_with_bracket)
    ]  # Add [1::2] if add the additional operation at the last step
    return bracket_start, bracket_end


def split_fragment_name(fragment_name):
    frag_type, frag_num, frag_charge, frag_loss = re.findall("([abcxyz])(\\d+)\\+(\\d+)-?(.*)", fragment_name)[0]
    return frag_type, int(frag_num), int(frag_charge), frag_loss


def split_prec(prec: str, keep_underscore: bool = False) -> typing.Tuple[str, int]:
    """
    Can not cover all cases, like
        OpenSwath will have . for n-term or c-term mod, while directly add charge to the last char of pep to get prec
        Spectronaut will have no . in pep text, while _ is always at the first and last positions
    Prec will have format like pep_charge, or pep.charge, or pepcharge, and can not be disdigushed
    This func only cover non-dot pep format. Means . is not used to indicate the n/c-term
    """
    if "." in prec:
        if (n := len(l := prec.split("."))) == 2:
            modpep, charge = l
        else:
            raise ValueError(
                f"Precursor has `.` in text. Expect having format like pep.charge, but {n} `.` were in text"
            )
    else:
        modpep, charge = prec[:-1], prec[-1]

    if charge.isdigit():
        charge = int(charge)
    else:
        raise ValueError(f"Precursor charge is expected as an integer. Now {charge} in precursor {prec}")

    if not keep_underscore:
        modpep = modpep.replace("_", "")
    return modpep, charge


def assemble_prec(modpep, charge):
    if not modpep.startswith("_"):
        modpep = f"_{modpep}_"
    return f"{modpep}.{charge}"


def split_mod(modpep, mod_ident="bracket"):
    if mod_ident == "bracket":
        mod_ident = ("[", "]")
    elif mod_ident == "parenthesis":
        mod_ident = ("(", ")")
    else:
        pass
    re_find_pattern = "(\\{}.+?\\{})".format(*mod_ident)
    re_sub_pattern = "\\{}.*?\\{}".format(*mod_ident)
    modpep = modpep.replace("_", "")
    mod_len = 0
    mod = ""
    for _ in re.finditer(re_find_pattern, modpep):
        _start, _end = _.span()
        mod += "{},{};".format(_start - mod_len, _.group().strip("".join(mod_ident)))
        mod_len += _end - _start
    stripped_pep = re.sub(re_sub_pattern, "", modpep)
    return stripped_pep, mod


def str_mod_to_list(mod):
    mod_list = [each_mod.split(",") for each_mod in mod.strip(";").split(";")]
    mod_list = [(int(_[0]), _[1]) for _ in mod_list]
    return mod_list


def add_mod(pep, mod, mod_processor):
    """
    mod_process is the ModOperation class
    """
    if mod:
        if isinstance(mod, str):
            mod = str_mod_to_list(mod)
        mod = sorted(mod, key=lambda x: x[0])
        mod_pep_list = []
        prev_site_num = 0
        for mod_site, mod_name in mod:
            mod_pep_list.append(pep[prev_site_num:mod_site])
            if mod_site != 0:
                mod_aa = mod_pep_list[-1][-1]
            else:
                mod_aa = pep[0]
            mod_pep_list.append(mod_processor(mod=mod_name, aa=mod_aa))
            prev_site_num = mod_site
        mod_pep_list.append(pep[prev_site_num:])
        mod_pep = "".join(mod_pep_list)
    else:
        mod_pep = pep
    mod_pep = f"_{mod_pep}_"
    return mod_pep


def fasta_title(title: str, title_type="uniprot"):
    title = title.lstrip(">")

    if "|" in title:
        ident = title.split("|")[1]
    else:
        ident = title.split(" ")[0]
    return ident


def join_seqtext_in_fasta(seq_text):
    return "".join(seq_text.split("\n"))


def join_seqlines_in_fasta(seq_lines):
    return "".join([_.strip("\n") for _ in seq_lines])
