#!/home/twinkle/venv/bin/python

import os
import sys
import threading
import re

import time
import locale

import shutil
import inspect
import traceback

import torch

import socket

from datetime import datetime

######################################################################
# LIBS

from twlog.Code import *
from twlog.Filters import Filter
from twlog.Formatters import Formatter, LogRecord
from twlog.Handlers import Handler
from twlog.Handlers.Ansi import AnsiHandler
from twlog.Handlers.Stream import StreamHandler
from twlog.Handlers.File import FileHandler
from twlog.util.AnsiColor import ansi

######################################################################
# BASIC CONFIG
_basicConfig = {
     "level": INFO,
       "fmt": "%(asctime)s %(message)s",
   "datefmt": "[%Y-%m-%d %H:%M:%S]",
  "handlers": [],
 "formatter": None,
}

######################################################################
# LOCKED CONFIG
_basicConfig_lock = threading.Lock()
_basicConfig_done = False

######################################################################
# CODE

_basicConfig["handlers"] = [RichHandler(level=INFO)]
_basicConfig["formatter"] =  Formatter()
for h in range(len(_basicConfig["handlers"])):
    _basicConfig["handlers"][h].setFormatter(_basicConfig["formatter"])

# Basic Configuration
def basicConfig(level:int = INFO, fmt: str = "%(message)s", datefmt: str = "[%Y-%m-%d %H:%M:%S]", handlers: list = None, formatter: Formatter = None):
    _basicConfig["level"] = level if level is not None and level in LOG_LEVEL else INFO
    _basicConfig["fmt"] = str(fmt) if fmt is not None and type(fmt) == 'str' else "%(message)s"
    _basicConfig["datefmt"] = str(datefmt) if datefmt is not None and type(datefmt) == 'str' else "[%Y-%m-%d %H:%M:%S]"
    # Handlers
    if handlers is None or len(handlers) == 0:
        _basicConfig["handlers"] = [RichHandler(level=INFO, stream=sys.stdout, stream_err=sys.stderr, markup=True, rich_tracebacks=True)]
    # Formatter
    _basicConfig["formatter"] = formatter if formatter is not None else Formatter(fmt=_basicConfig["format"], datefmt=_basicConfig["datefmt"])
    for h in range(len(_basicConfig["handlers"])):
        _basicConfig["handlers"][h].setFormatter(_basicConfig["formatter"])
    # ^^;
    return _basicConfig.copy()

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["basicConfig"]

""" __DATA__

__END__ """
