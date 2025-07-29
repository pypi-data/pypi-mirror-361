import inspect
import os
import re
import sys
from typing import Any


def load_py_file(file_path, remove_insert_path="new"):
    """
    :param file_path:

    :param remove_insert_path:
        'any' to remove inserted path even the path is in path list before performing this function
        'new' (default) to remove inserted path from sys path list if this path was not in list before
        False to do nothing
    """
    # TODO remove inserted path?
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_name_no_suffix = os.path.splitext(os.path.basename(file_name))[0]
    sys.path.insert(-1, file_dir)
    content = {}
    try:
        exec(f"import py file {file_name}", {}, content)
    except ModuleNotFoundError:
        raise FileNotFoundError(f"Not find input file {file_name} with basename {file_name_no_suffix} in {file_dir}")
    return content["content"]


def get_var_default_args(
    var,
    assign_to_empty: Any = None,
    get_all_args_from_parent: bool = True,
    exclude_self: bool = True,
):
    if inspect.isfunction(var):
        args = {
            name: param.default if param.default is not inspect.Parameter.empty else assign_to_empty
            for name, param in inspect.signature(var).parameters
        }
    elif inspect.isclass(var):
        pass
    elif isinstance(var, object):
        var = var.__class__
    else:
        raise ValueError(f"To compare args, var must be a class, function, or an initialized object, got {type(var)}")

    if get_all_args_from_parent:
        all_cls = []
        # inspect.getmro will return a tuple of classes in the order of inheritance,
        # with the input class as first and the basic `object` as the last
        for each_cls in inspect.getmro(var):
            if each_cls is object:
                continue
            all_cls.append(each_cls)
    else:
        all_cls = [var]
    args = {}
    for each_cls in all_cls:
        init = getattr(each_cls, "__init__", None)
        if init:
            sig = inspect.signature(init)
            for name, param in sig.parameters.items():
                if name != "self" and name not in args:
                    args[name] = param.default if param.default is not inspect.Parameter.empty else assign_to_empty
    return args


def varname(var):
    """
    https://stackoverflow.com/questions/592746/how-can-you-print-a-variable-name-in-python
    Call this function to traceback required code content, and extract variable name via re

    Example:
    Traceback(filename='<ipython-input-37-5fa84b05d0d4>', lineno=2, function='<module>', code_context=['b = varname(a)\n'], index=0)
    This can get content in "varname(...)"
    """
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r"\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)", line)
    if m:
        return m.group(1)
