# -*- coding: utf-8 -*-
# __init__.py

__version__ = "1.1.0"

from .binning import reBin
from .git import checkRepo, isNBstripoutActivated, isNBstripoutInstalled, isRepo
from .readdata import readdata
from .readdata import readdata as readPDH
from .utils import setLocaleUTF8
from .widgets import PathSelector, showBoolStatus

setLocaleUTF8()
