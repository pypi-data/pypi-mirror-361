import os


def c_c(c):
    return " ".join([_ if os.sep not in _ else f'"{_}"' for _ in c.split(" ") if _ != ""])
