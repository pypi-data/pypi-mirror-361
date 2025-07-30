"""
OS utilities and helpers for jgtcore

Core OS-related functions migrated from jgtutils including:
- TLID (Time/Location ID) range handling
- Instrument and timeframe conversion
- File path and filename utilities
"""

import datetime
import os
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional

# External dependency - TLID library
try:
    import tlid
    HAS_TLID = True
except ImportError:
    tlid = None
    HAS_TLID = False

# Optional dateutil support
try:
    from dateutil.parser import parse
    from dateutil.relativedelta import relativedelta
    HAS_DATEUTIL = True
except ImportError:
    parse = None
    relativedelta = None
    HAS_DATEUTIL = False


# TLID Range Functions

def tlid_range_to_start_end_datetime(tlid_range: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Convert TLID range string to start and end datetime objects.
    
    Args:
        tlid_range: TLID range string (e.g., "2301010000_2301312359" or just "23")
        
    Returns:
        Tuple of (start_datetime, end_datetime) or (None, None) if invalid
    """
    # Support inputting just a Year
    if len(tlid_range) == 4 or len(tlid_range) == 2:
        start_str = tlid_range + "0101" + "0000"
        end_str = tlid_range + "1231" + "2359"
    else:
        # Normal support start_end
        try:
            start_str, end_str = tlid_range.split("_")
        except:
            print('TLID ERROR - make sure you used a "_"')
            return None, None
    
    date_format_start = "%y%m%d%H%M"
    date_format_end = "%y%m%d%H%M"
    
    if len(start_str) == 4 or len(start_str) == 2:
        start_str = start_str + "0101" + "0000"
    if len(end_str) == 4 or len(end_str) == 2:
        end_str = end_str + "1231" + "2359"
    
    if len(start_str) == 6:
        start_str = start_str + "0000"
    if len(end_str) == 6:
        end_str = end_str + "2359"
   
    if len(start_str) == 8:
        start_str = start_str + "0000"
    if len(end_str) == 8:
        end_str = end_str + "2359"
        
    if len(start_str) == 12:
        date_format_start = "%Y%m%d%H%M"
    if len(end_str) == 12:
        date_format_end = "%Y%m%d%H%M"
   
    try:
        start_dt = datetime.strptime(start_str, date_format_start)
        end_dt = datetime.strptime(end_str, date_format_end)
        return start_dt, end_dt
    except ValueError:
        return None, None


def tlid_range_to_jgtfxcon_start_end_str(tlid_range: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Convert TLID range to JGT FX connection format strings.
    
    Args:
        tlid_range: TLID range string
        
    Returns:
        Tuple of (start_str, end_str) in FX connection format or (None, None) if invalid
    """
    date_format_fxcon = '%m.%d.%Y %H:%M:%S'
    start_dt, end_dt = tlid_range_to_start_end_datetime(tlid_range)
    
    if start_dt is None or end_dt is None:
        return None, None
    else:
        return str(start_dt.strftime(date_format_fxcon)), str(end_dt.strftime(date_format_fxcon))


def tlid_dt_to_string(dt: datetime) -> str:
    """
    Convert datetime to TLID string format.
    
    Args:
        dt: Datetime object
        
    Returns:
        TLID string in format YYMMDDHHMM
    """
    return dt.strftime("%y%m%d%H%M")


def tlidmin_to_dt(tlid_str: str) -> Optional[datetime]:
    """
    Convert TLID string to datetime object.
    
    Args:
        tlid_str: TLID string in format YYMMDDHHMM
        
    Returns:
        Datetime object or None if invalid
    """
    date_format = "%y%m%d%H%M"
    try:
        tlid_dt = datetime.strptime(tlid_str, date_format)
        return tlid_dt
    except ValueError:
        pass
    
    return None


# Instrument and Timeframe Conversion Functions

def i2fn(i: str) -> str:
    """
    Convert instrument to filename-compatible string.
    
    Args:
        i: Instrument string (e.g., "EUR/USD")
        
    Returns:
        Filename-compatible string (e.g., "EUR-USD")
    """
    return i.replace("/", "-")


def fn2i(ifn: str) -> str:
    """
    Convert filename string to instrument-compatible string.
    
    Args:
        ifn: Filename string (e.g., "EUR-USD")
        
    Returns:
        Instrument string (e.g., "EUR/USD")
    """
    return ifn.replace("-", "/")


def t2fn(t: str) -> str:
    """
    Convert timeframe to filename-compatible string.
    
    Args:
        t: Timeframe string (e.g., "m1")
        
    Returns:
        Filename-compatible timeframe (e.g., "mi1")
    """
    t_fix = t if t != "m1" else t.replace("m1", "mi1")
    return t_fix


def fn2t(t: str) -> str:
    """
    Convert filename timeframe to timeframe-compatible string.
    
    Args:
        t: Filename timeframe string (e.g., "mi1" or "min1")
        
    Returns:
        Timeframe string (e.g., "m1")
    """
    t_fix = t if t != "mi1" else t.replace("mi1", "m1")
    t_fix = t_fix if t_fix != "min1" else t_fix.replace("min1", "m1")
    return t_fix


def topovfn(i: str, t: str, separator: str = "_") -> str:
    """
    Create POV filename from instrument and timeframe.
    
    Args:
        i: Instrument string
        t: Timeframe string
        separator: Separator character
        
    Returns:
        POV filename string
    """
    return f"{i2fn(i)}{separator}{t2fn(t)}"


def fn2pov(fn: str, separator: str = "_") -> Tuple[str, str]:
    """
    Convert filename to POV (instrument, timeframe) tuple.
    
    Args:
        fn: Filename string
        separator: Separator character
        
    Returns:
        Tuple of (instrument, timeframe)
    """
    arr = fn.split(separator)
    i = fn2i(arr[0])
    t = fn2t(arr[1])
    return i, t


# Advanced TLID Range Calculation

def get_dt_format_pattern(end_datetime: str) -> str:
    """
    Detect datetime format pattern from string.
    
    Args:
        end_datetime: Datetime string
        
    Returns:
        Format pattern string
        
    Raises:
        ValueError: If format cannot be detected
    """
    formats = [
        ("%Y-%m-%d", r"\d{4}-\d{2}-\d{2}$"),
        ("%y-%m-%d", r"\d{2}-\d{2}-\d{2}$"),
        ("%Y-%m-%d %H:%M", r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"),
        ("%y-%m-%d %H:%M", r"\d{2}-\d{2}-\d{2} \d{2}:\d{2}$"),
    ]
    dt_pattern = "%y-%m-%d"  # default

    # Try to match the end_datetime string with each pattern
    for date_format, pattern in formats:
        if re.match(pattern, end_datetime):
            dt_pattern = date_format
            break
    else:
        raise ValueError(f"Invalid date format in end_datetime: {end_datetime}")

    return dt_pattern


def calculate_start_datetime(end_datetime: str, timeframe: str, periods: int) -> datetime:
    """
    Calculate start datetime from end datetime, timeframe, and periods.
    
    Args:
        end_datetime: End datetime string
        timeframe: Timeframe string (e.g., "H1", "D1", "m15")
        periods: Number of periods to go back
        
    Returns:
        Start datetime object
    """
    date_format = get_dt_format_pattern(end_datetime)
    
    # Parse end_datetime string into datetime object
    end_dt = datetime.strptime(end_datetime, date_format)
    
    # If the year is less than 100, add 2000 to it to get the correct century
    if end_dt.year < 100:
        end_dt = end_dt.replace(year=end_dt.year + 2000)
    
    # Check if timeframe is in hours
    if timeframe.startswith('H'):
        # Convert timeframe from hours to minutes
        timeframe_minutes = int(timeframe[1:]) * 60
    elif timeframe.startswith('D'):
        # Convert timeframe from days to minutes
        timeframe_minutes = int(timeframe[1:]) * 24 * 60
    elif timeframe.startswith('W'):
        # Convert timeframe from weeks to minutes
        timeframe_minutes = int(timeframe[1:]) * 7 * 24 * 60
    elif timeframe.startswith('M'):
        # Convert timeframe from months to minutes
        # Assume an average of 30 days per month
        timeframe_minutes = int(timeframe[1:]) * 30 * 24 * 60
    elif timeframe.startswith('m'):
        # Convert timeframe from minutes
        timeframe_minutes = int(timeframe[1:])
    else:
        # Assume timeframe is already in minutes
        timeframe_minutes = int(timeframe)
    
    # Convert timeframe from minutes to seconds
    timeframe_seconds = timeframe_minutes * 60
    # Calculate total seconds for all periods
    total_seconds = timeframe_seconds * periods
    # Calculate start datetime
    start_datetime = end_dt - timedelta(seconds=total_seconds)
    
    return start_datetime


def calculate_tlid_range(end_datetime: str, timeframe: str, periods: int) -> str:
    """
    Calculate TLID range from end datetime, timeframe, and periods.
    
    Args:
        end_datetime: End datetime string
        timeframe: Timeframe string
        periods: Number of periods to go back
        
    Returns:
        TLID range string in format "start_tlid_end_tlid"
        
    Raises:
        ImportError: If tlid library is not available
    """
    if not HAS_TLID:
        raise ImportError("tlid library is required for calculate_tlid_range function")
    
    # Calculate start datetime
    start_datetime = calculate_start_datetime(end_datetime, timeframe, periods)
    
    dt_pattern = get_dt_format_pattern(end_datetime)
    start_datetime_formatted = start_datetime.strftime(dt_pattern)
    
    # Format start and end datetime to tlid format
    start_tlid = tlid.fromdtstr(start_datetime_formatted)
    end_tlid = tlid.fromdtstr(end_datetime)
    
    # Return tlid range
    return f"{start_tlid}_{end_tlid}"


# File Naming Utilities

def mk_fn_range(instrument: str, timeframe: str, start: datetime, end: datetime, ext: str = "csv") -> str:
    """
    Create filename with range from instrument, timeframe, and datetime range.
    
    Args:
        instrument: Instrument string
        timeframe: Timeframe string
        start: Start datetime
        end: End datetime
        ext: File extension
        
    Returns:
        Filename string with range
    """
    _tf = timeframe
    _i = instrument.replace("/", "-")
    if timeframe == "m1":
        _tf = timeframe.replace("m1", "mi1")  # differentiate with M1
    start_str = tlid_dt_to_string(start)
    end_str = tlid_dt_to_string(end)
    _fn = f"{_i}_{_tf}_{start_str}_{end_str}.{ext}"
    _fn = _fn.replace("..", ".")
    _fn = _fn.replace("/", "-")
    return _fn


# Utility Functions

def ensure_directory_exists(filepath: str) -> str:
    """
    Ensure directory exists for a given filepath.
    
    Args:
        filepath: File path or directory path
        
    Returns:
        Directory path that was created/verified
    """
    # Detect if the filepath is a directory or a file
    is_probably_a_filepath = len(filepath) > 4 and filepath[-4] == "."
    if os.path.isfile(filepath) or is_probably_a_filepath:
        directory = os.path.dirname(filepath)
    else:
        directory = filepath
    
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return directory


__all__ = [
    # TLID range functions
    'tlid_range_to_start_end_datetime',
    'tlid_range_to_jgtfxcon_start_end_str',
    'tlid_dt_to_string',
    'tlidmin_to_dt',
    
    # Instrument/timeframe conversion
    'i2fn', 'fn2i', 't2fn', 'fn2t',
    'topovfn', 'fn2pov',
    
    # Advanced TLID calculation
    'get_dt_format_pattern',
    'calculate_start_datetime',
    'calculate_tlid_range',
    
    # File naming utilities
    'mk_fn_range',
    'ensure_directory_exists',
    
    # Constants
    'HAS_TLID',
    'HAS_DATEUTIL',
]