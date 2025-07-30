#!/home/twinkle/venv/bin/python

import os
import sys
import threading
import re


import shutil
import inspect
import traceback

from datetime import datetime

######################################################################
# LIBS

from twlog.util.Code import *
from twlog.util.ANSIColor import ansi
from twlog.Formatters import Formatter, LogRecord

######################################################################
# Classes - handlers

class Handler():
    # Initialization
    def __init__(self, level=NOTSET) -> None:
        super(Handler, self).__init__()
        # Initial Level
        self.level = level if level is not None and level in LOG_LEVEL else INFO
        self.filter = None
        self.formatter = None
    def createLock(level):
        return True
    def acquire(level):
        return True
    def release(level):
        return True
    # Level
    def setLevel(self, level: int = 0):
        self.level = level if level in LOG_LEVEL else self.INFO
    # Filters
    def addFilter(self, filter):
        self.filter = filter if filter is not None else None
    def removeFilter(self, filter):
        self.filter = None
    def filter(self):
        return True
    # Flush
    def flush(self):
        return True
    def close(self):
        return True
    def handle(self, records):
        return True
    def handleError(self, records):
        return True
    # Formatter
    def setFormatter(self, fmt: Formatter = None):
        self.formatter = fmt if fmt is not None else None
    def format(self, record):
        return self.formatter.format(record)
    def emit(self, record):
        print(record)

class NullHandler(Handler):
    # Initialization
    def __init__(self, level=INFO) -> None:
        super(NullHandler, self).__init__(level=level)
    def emit(self, record):
        return None
    def handle(self, record):
        return None
    def createLock(self):
        return None

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["Handler", "NullHandler"]

""" __DATA__

__END__ """
