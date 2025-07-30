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

import socket

from datetime import datetime

######################################################################
# LIBS

from twlog.util.Code import *
from twlog.util.ANSIColor import ansi
from twlog.Filters import Filter
from twlog.Formatters import Formatter, LogRecord
from twlog.Handlers import Handler
from twlog.Handlers.ANSI import ANSIHandler

######################################################################
# REGISTRY
_logger_registry = {}

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
# RootLogger - really fake root logger

class root():
    # Initialization
    def __init__(self, level=INFO, propagate=False, parent=None, disabled=False, *args, **kwargs) -> None:
        # Arguments
        self._args = args
        self._kwargs = kwargs
        # Name
        self.name = 'root'
        # Log Level
        self.level = level if level is not None and level in LOG_LEVEL else INFO
        # Handlers
        self.handlers = _basicConfig["handlers"]
        # Current
        self.parent = parent if parent is not None else None
        self.propagate = bool(propagate) if propagate is True else False
        self.disabled = bool(disabled) if disabled is True else False
    # Root Fuynctions
    def isEnabledFor(self, level):
        return True
    def getEffectiveLevel(self):
        return NOTSET
    def getChild(self, suffix):
        ret = []
        for key in _logger_registry.keys():
            if key != suffix and re.search(_logger_registry[key], suffix):
                ret.append(key)
        return ret
    def getChildren(self):
        ret = []
        for key in _logger_registry.keys():
            if key != self.name and re.search(_logger_registry[key], self.name):
                ret.append(key)
        return ret
    def exception(msg, *args, **kwargs):
        return True
    def setHandler(self, hdlr):
        self.handlers = hdlr
    def addHandler(self, hdlr):
        self.handlers.append(hdlr)
    def removeHandler(self, hdlr):
        for h in range(len(self.handlers)):
            if hdlr == self.handlers[h]:
                self.handler.pop(h); break
    def handle(self, record):
        for h in range(len(self.handlers)):
            self.handlers[h].emit(record)
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        return LogRecord(name=name, level=level, fn=None, lno=None, msg=msg, args=self._args, exc_info=None, func=func, extra=extra, sinfo=sinfo)
    def hasHandlers(self):
        return True if len(self.handlers) != 0 else False
    def Formatter(self):
        return self.formatter
    # Caller
    def findCaller(self, stack_info=False, stack_level=1):
        caller_frame = inspect.currentframe().f_back
        caller_class = caller_frame.f_locals.get('self', None).__class__
        return caller_class.__name__
    def test(self, message: any = None):
        for l in LOG_LEVEL.keys():
            if l == "NOTSET": continue
            self.__call__((message if message is not None else l), level=LOG_LEVEL[l], title=l)
    # Logging
    def log(self, message:any = None, level: int = 20, title: str = None):
        title = title if title is not None else 'LOG'
        if self.propagate is True and self.parent is not None:
            self.parent.log(message=message, level=level, title=title)
    # Array Disaddembly
    def msg_disassembly(self, message):
        if hasattr(message, 'tolist'):
            try: message = str(message.tolist())
            except: message = str(message)
        elif hasattr(message, 'item'):
            try: message = str(message.item())
            except: message = str(message)
        else: message = str(message)
        return message
    # Promise for Console
    def logging(self, datefmt: str = None, msgfmt: str = None, message: str = None, level: int = 20, title: str = None):
        # Title Setting
        title = str(title) if title is not None else uc(self.name)
        level = level if level is not None else self.level
        # numpy.ndarray, torch.Tensor, Jax, ...
        message = message if isinstance(message, str) else self.msg_disassembly(message)
        records = self.makeRecord(title, level, None, None, message, self._args, None, func=None, extra=None, sinfo=None)
        # Handlers
        self.handle(records)
    # Wrappers
    def debug(self, message:any = None, level=10, title=None):
        title = title if title is not None else 'DEBUG'
        self.logging(message=message, level=level, title=title)
    def info(self, message:any = None, level=20, title=None):
        title = title if title is not None else 'INFO'
        self.logging(message=message, level=level, title=title)
    def warn(self, message:any = None, level=30, title=None):
        title = title if title is not None else 'WARN'
        self.logging(message=message, level=level, title=title)
    def error(self, message:any = None, level=40, title=None):
        title = title if title is not None else 'ERROR'
        self.logging(message=message, level=level, title=title)
    def critical(self, message:any = None, level=50, title=None):
        title = title if title is not None else 'CRITICAL'
        self.logging(message=message, level=level, title=title)
    def notice(self, message:any = None, level=25, title=None):
        title = title if title is not None else 'NOTICE'
        self.logging(message=message, level=level, title=title)
    def issue(self, message:any = None, level=60, title=None):
        title = title if title is not None else 'ISSUE'
        self.logging(message=message, level=level, title=title)
    def matter(self, message:any = None, level=70, title=None):
        title = title if title is not None else '\x27O\x27 MATTER'
        self.logging(message=message, level=level, title=title)
    #========================================
    def __call__(self, message:any = None, level=None, title=None):
        level = level if level is not None else self.level
        if level == NOTSET: self.log(level, message, title=title)
        elif level == DEBUG: self.debug(message, level=level, title=title)
        elif level == WARN: self.warn(message, level=level, title=title)
        elif level == ERROR: self.error(message, level=level, title=title)
        elif level == NOTICE: self.notice(message, level=level, title=title)
        elif level == ISSUE: self.issue(message, level=level, title=title)
        elif level == MATTER: self.matter(message, level=level, title=title)
        else: self.info(message, level=level, title=title)

######################################################################
# Logger
class logging(root, ansi):
    # Initialization
    def __init__(self, name=None, level=INFO, propagate=False, parent=None, disabled=False, handlers=[], *args, **kwargs) -> None:
        super(logging, self).__init__(level=level, propagate=propagate, parent=parent, disabled=False)
        self.name = str(name) if name is not None else __name__
    # Safe Update
    def safedate(self, src: dict, dest: dict) -> dict:
        for key in dest.keys():
            if key not in src:
                src[key] = dest[key]
    # Export Log Level
    def export_global_loglevel(self, name=None):
        if name is not None:
            c = sys.modules.get(name)
            if c is None:
                c = sys.modules.get(_get_caller_class_name())
                if c is not None:
                    # Update
                    safedate(src=c.__dict__, dest=LOG_LEVEL)
    #========================================
    # Pixie: 🧚✨✨✨✨✨
    def pixie(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        m = f"🧚✨✨✨ {ansi.start}{ansi.fore_light_cyan};{ansi.text_on_blink};{ansi.text_on_bold}m{b} {ansi.reset}✨✨ "
        m += ", ".join(a)
        print(f"{m}")
    #========================================
    # Print for as options pair values. You guys not yet see EBI 🍤🍤🍤🍤
    def popts(self, b, *t):
        b = str(b)
        a = [""] * len(t) 
        for i in range(len(t)):
            a[i] = str(t[i])
        m = f"\x1b[1m{b}:\x1b[0m "
        m += ", ".join(a)
        print(f"{m}")
    #========================================
    # No All Breaks ∞ Looping
    def psolo(self, *t):
        for i in range(len(t)):
            print(t[i], end='')

######################################################################
# CODE

_basicConfig["handlers"] = [ANSIHandler(level=INFO)]
_basicConfig["formatter"] =  Formatter()
_basicConfig["filter"] =  Filter()
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

# ChatGPT
def getLogger(name=None):
    if not name:
        name = "__main__"
    if name in _logger_registry:
        return _logger_registry[name]

    parent_name = ".".join(name.split(".")[:-1]) if "." in name else None
    parent = _logger_registry.get(parent_name) if parent_name else None

    logger = logging(name=name, level=_basicConfig["level"], parent=parent)
    _logger_registry[name] = logger
    return logger

######################################################################
# CONFIG互換関数

def RootLogger(*args, force=False, **kwargs):
    """
    logging.basicConfig 互換
    最初に一度だけ設定し、root を構成します。
    """
    global _basicConfig_done, root
    with _basicConfig_lock:
        if _basicConfig_done and not force:
            return
        basicConfig(*args, **kwargs)
        root = getLogger("__main__")
        root.addFilter(filter("__main__"))
        _basicConfig_done = True

######################################################################
# getLogger

root = root()

######################################################################
# ログレベル関数互換 (logging.info など)

def debug(*args, **kwargs):
    root.debug(*args, **kwargs)
def info(*args, **kwargs):
    root.info(*args, **kwargs)
def warning(*args, **kwargs):
    root.warning(*args, **kwargs)
def warn(*args, **kwargs):
    root.warn(*args, **kwargs)
def error(*args, **kwargs):
    root.error(*args, **kwargs)
def critical(*args, **kwargs):
    root.critical(*args, **kwargs)
def notice(*args, **kwargs):
    root.notice(*args, **kwargs)
def issue(*args, **kwargs):
    root.issue(*args, **kwargs)
def matter(*args, **kwargs):
    root.matter(*args, **kwargs)
def exception(*args, **kwargs):
    root.exception(*args, exc_info=True, **kwargs)

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["getLogger", "logging", "debug", "info", "warn", "warning", "error", "critical", "notice", "issue", "matter", "exception"]

""" __DATA__

__END__ """
