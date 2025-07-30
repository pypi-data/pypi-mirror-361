from datetime import datetime
from typing import Callable

import humanfriendly

from .sacct_fields import SACCT_FIELDS


def _identity(arg: str) -> str:
    return arg


def _str_to_float_to_int(arg: str) -> int:
    return int(float(arg))


def _dhhmmss_to_seconds(arg: str) -> int:
    """
    Supports both `HH:MM:SS` and `D-HH:MM:SS`.
    """
    if "-" in arg:
        days, hhmmss = arg.split("-")
    else:
        days = "0"
        hhmmss = arg[:]
    hh, mm, ss = hhmmss.split(":")[:]
    return int(days) * 3600 * 24 + int(hh) * 3600 + int(mm) * 60 + int(ss)


def _str_to_datetime(arg: str) -> str:
    return datetime.fromisoformat(arg).isoformat()


def _str_to_bytes(arg: str) -> int:
    return humanfriendly.parse_size(arg)


def _str_to_bytes_to_friendly(arg: str) -> str:
    return humanfriendly.format_size(_str_to_bytes(arg))


SACCT_FIELD_PARSERS: dict[str, Callable] = {
    field: _identity for field in SACCT_FIELDS
}

for field in [
    "JobID",
    "NCPUS",
    "NTasks",
    "MinCPUTask",
    "MaxDiskReadTask",
    "MaxDiskWriteTask",
    "MaxPagesTask",
    "MaxRSSTask",
    "MaxVMSizeTask",
    "CPUTimeRaw",
    "ElapsedRaw",
    "NCPUS",
]:
    SACCT_FIELD_PARSERS[field] = _str_to_float_to_int

for field in ["Elapsed", "CPUTime", "MinCPU", "AveCPU"]:
    SACCT_FIELD_PARSERS[field] = _dhhmmss_to_seconds

for field in ["Submit", "Start", "End"]:
    SACCT_FIELD_PARSERS[field] = _str_to_datetime

for field in [
    "MaxDiskWrite",
    "MaxDiskRead",
    "MaxRSS",
    "MaxVMSize",
    "AveDiskWrite",
    "AveDiskRead",
    "AveRSS",
    "AveVMSize",
]:
    SACCT_FIELD_PARSERS[field] = _str_to_bytes_to_friendly
