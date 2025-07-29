# -*- coding: utf-8 -*-
# utils.py

import contextlib
import copy
import itertools
import locale
import os
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np

indent = "    "


def setLocaleUTF8():
    """Fix the Jupyter locale which is not UTF-8 by default on some systems (older Windows?)."""
    locOld = locale.getpreferredencoding(False).lower()

    def getpreferredencoding(do_setlocale=True):
        return "utf-8"

    locale.getpreferredencoding = getpreferredencoding
    locNew = locale.getpreferredencoding(False)
    if locOld != locNew:
        print(f"Updated locale from {locOld} -> {locNew}.")


def isLinux():
    return platform.system().lower() in "linux"


def isMac():
    return platform.system().lower() in "darwin"


def isWindows():
    return platform.system().lower() in "windows"


def isList(obj):
    """Return true if the provided object is list-like including a numpy array
    but not a string.

    >>> isList([1, 2, 'a'])
    True
    >>> isList(tuple((1, 2, 'a')))
    True
    >>> import numpy
    >>> isList(numpy.arange(5))
    True
    >>> isList("dummy")
    False
    >>> isList(None)
    False
    """
    return isinstance(obj, (list, tuple, np.ndarray))


def shortenWinPath(path):
    if not isWindows():
        return path
    import win32api

    return win32api.GetShortPathName(path)


def appendToPATH(parentPath, subdirs=None):
    """Adds the given path with each subdirectory to the PATH environment variable."""
    if not os.path.isdir(parentPath):
        return  # nothing to do
    if subdirs is None:
        subdirs = ["."]
    for path in subdirs:
        path = os.path.realpath(os.path.join(parentPath, *path.split("/")))
        print(indent, path, "\t[{}]".format(os.path.isdir(path)))
        if path in os.environ["PATH"]:
            continue
        os.environ["PATH"] += ";" + path


def checkWinFor7z():
    """Extend the PATH environment variable for access to the 7-zip executable."""
    if not isWindows():
        return  # tests below are intended for Windows
    sevenzippath = r"C:\Program Files\7-Zip"
    if not os.path.isdir(sevenzippath):
        print(
            "7-Zip not found in '{}'.\n".format(sevenzippath)
            + "7-Zip is required for managing data files and results!."
        )
        return
    print("Adding the following directory to $PATH:")
    appendToPATH(sevenzippath)
    print("\nUpdated PATH:")
    for path in os.environ["PATH"].split(";"):
        print(indent, path)


def extract7z(fn, workdir=None):
    assert os.path.isfile(os.path.join(workdir, fn)), "Provided 7z archive '{}' not found!".format(
        fn
    )
    print("Extracting archived McDLS results:")
    proc = subprocess.run(
        ["7z", "x", fn],
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(proc.stdout.decode(errors="ignore"))
    if len(proc.stderr):
        print("## stderr:\n", proc.stderr.decode(errors="ignore"))


# https://stackoverflow.com/a/13847807
@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(previous_dir)


def setPackage(globalsdict):
    """Sets the current directory of the notebook as python package
    to make relative module imports work.
    Usage: `setPackage(globals())`"""
    path = Path().resolve()
    searchpath = str(path.parent)
    if searchpath not in sys.path:
        sys.path.insert(0, searchpath)
    globalsdict["__package__"] = path.name
    globalsdict["__name__"] = path.name
    print(f"Setting the current directory as package '{path.name}':\n  {path}.")


def grouper(iterable, n, fillvalue=None):
    """Returns an iterator over a list of tuples (grouping) for a given flat iterable."""
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def fmtErr(val, std, precision=2, width=None):
    """Formats a given value and its std. deviation to physics notation, e.g. '1.23(4)'."""
    if width is None:
        width = ""
    fmt = "{:" + str(width) + "." + str(precision) + "f}({:.0f})"
    # print("fmtErr val:", val, "std:", std)
    return fmt.format(val, std * 10 ** (precision))


def updatedDict(d, key, value):
    """Implements the \\|= operator for dict in Python version <3.9."""
    dd = copy.copy(d)
    dd[key] = value
    return dd
