import traceback
from helpers import resource_path
import sys
import time


def log_crash(e: Exception):
    error_filepath = resource_path(f"crash_report_{time.time()}.log")
    tb = traceback.format_tb(sys.exc_info()[2])
    with open(error_filepath, 'w') as f:
        f.write("\n".join(tb) + "\n")
        f.write(str(e))


def log_error(e: Exception):
    error_filepath = resource_path(f"crash_logs.log")
    tb = traceback.format_tb(sys.exc_info()[2])
    with open(error_filepath, 'a') as f:
        f.write("\n".join(tb) + "\n")
        f.write(str(e))
