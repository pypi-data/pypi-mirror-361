#!/home/twinkle/venv/bin/python

import sys
import shutil

######################################################################
# LIBS

from twlog.util.Code import *
from twlog.Formatters import Formatter, LogRecord
from twlog.Handlers import Handler

######################################################################
# Classes - handlers

class StreamHandler(Handler):
    # Initialization
    def __init__(self, level=INFO, stream=sys.stdout, stream_err=sys.stderr) -> None:
        super(StreamHandler, self).__init__(level=level)
        self.stream = stream if stream is not None else sys.stdout
        self.stream_err = stream_err if stream_err is not None else sys.stderr
        self.terminator = '\n'
    def emit(self, record):
        # Fromat
        record = self.format(record)
        # Initialize
        mf = f"{record['asctime']} |{record['name']}| {record['message']}"
        ml = len(mf)
        # filename and lineno
        if record["level"] >= 30:
            fl = f" ({record['filename']}:{record['lineno']})"
            ml += len(fl)
            ts = shutil.get_terminal_size().columns
            df = ts - ml
            if df > 0: mf += (" " * df)
            mf += fl
            print(mf, file=self.stream_err)
        # ^^;
        else:
            print(mf, file=self.stream)
    # Testing
    def flush(self):
        return True
    def setStrteam(self, stream):
        return True

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["StreamHandler"]

""" __DATA__

__END__ """
