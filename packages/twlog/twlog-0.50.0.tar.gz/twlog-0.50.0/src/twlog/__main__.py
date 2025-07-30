#!/home/twinkle/venv/bin/python

######################################################################
# LIBS

from twlog.util.Code import *
from twlog.util.ANSIColor import ansi
from twlog.util import *
from twlog import getLogger
from twlog.Filters import Filter
from twlog.Formatters import Formatter, LogRecord
from twlog.Handlers import Handler
from twlog.Handlers.ANSI import ANSIHandler

#####################################################################
# CODE

# Define True Logger
#twlog.util.Code.export_global_loglevel(__name__)
logger = getLogger(__name__)

logger.test()

priny("priny", "priny")
pixie("pixie", "pixie")
prain("prain", "prain")
paint("paint", "paint")
plume("plume", "plume")
prank("prank", "prank")
prown("prown", "prown")
prism("prism", "prism")

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = [""]

""" __DATA__

__END__ """
