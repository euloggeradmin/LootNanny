import os
import sys
from datetime import datetime
import time


def resource_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def dt_to_ts(dt: datetime) -> float:
    return time.mktime(dt.timetuple())


def ts_to_dt(ts: float) -> datetime:
    return datetime.fromtimestamp(ts)


def get_app_data_path() -> str:
    path = os.path.join(os.sep, os.path.expanduser("~"), "AppData", "Local", "EULogger")
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def format_filename(fn: str) -> str:
    return os.path.join(get_app_data_path(), fn)
