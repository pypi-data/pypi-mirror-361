#!/home/twinkle/venv/bin/python

import sys
import shutil

######################################################################
# LIBS

from twlog.util.Code import *
from twlog.util.ANSIColor import ansi
from twlog.Formatters import Formatter, LogRecord
from twlog.Handlers import Handler

######################################################################
# Classes - handlers

class ANSIHandler(Handler):
    # Initialization
    def __init__(self, level=INFO, stream=sys.stdout, stream_err=sys.stderr, markup=True, rich_tracebacks=True) -> None:
        super(ANSIHandler, self).__init__(level=level)
        self.stream = stream if stream is not None else sys.stdout
        self.stream_err = stream_err if stream_err is not None else sys.stderr
        self.markup = True if markup is True else False
        self.rich_tracebacks = True if rich_tracebacks is True else False
        self.terminator = '\n'
    def emit(self, record):
        # Fromat
        record = self.format(record)
        # Rich ?
        if self.markup is True:
            # Rich
            if record['level'] == DEBUG:
                datefmt = f"{ansi.start}{ansi.fore_white};{ansi.text_on_bold}m"
                namefmt = f"{ansi.start}{ansi.back_light_gray};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record['level'] == WARN:
                datefmt = f"{ansi.start}{ansi.fore_light_yellow};{ansi.text_on_bold}m"
                namefmt = f"{ansi.start}{ansi.back_yellow};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record['level'] == ERROR:
                datefmt = f"{ansi.start}{ansi.fore_light_red};{ansi.text_on_bold}m"
                namefmt = f"{ansi.start}{ansi.back_red};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record['level'] == CRITICAL:
                datefmt = f"{ansi.start}{ansi.fore_red};{ansi.text_on_bold}m"
                namefmt = f"{ansi.start}{ansi.back_light_red};{ansi.fore_black};{ansi.text_on_bold}m"
            elif record['level'] == NOTICE:
                datefmt = f"{ansi.start}{ansi.fore_light_green};{ansi.text_on_bold}m"
                namefmt = f"{ansi.start}{ansi.back_green};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record['level'] == ISSUE:
                datefmt = f"{ansi.start}{ansi.fore_light_magenta};{ansi.text_on_bold}m"
                namefmt = f"{ansi.start}{ansi.back_purple};{ansi.fore_white};{ansi.text_on_bold}m"
            elif record['level'] == MATTER:
                datefmt = f"{ansi.start}{ansi.fore_white};{ansi.text_on_bold}m"
                namefmt = f"{ansi.start}{ansi.back_light_white};{ansi.fore_black};{ansi.text_on_bold}m"
            # Defaults (INFO)
            else:
                datefmt = f"{ansi.start}{ansi.fore_cyan};{ansi.text_on_bold}m"
                namefmt = f"{ansi.start}{ansi.back_blue};{ansi.fore_white};{ansi.text_on_bold}m"
            # Initialize
            mf = f"{datefmt}{record['asctime']}{ansi.reset} {namefmt}{record['name']}{ansi.reset} {record['message']}"
            ml = 2 + len(record['asctime']) + len(record['name']) + len(record['message']) # + X # if wants SP
        # No Rich
        else:
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
__all__ = ["ANSIHandler"]

""" __DATA__

__END__ """
