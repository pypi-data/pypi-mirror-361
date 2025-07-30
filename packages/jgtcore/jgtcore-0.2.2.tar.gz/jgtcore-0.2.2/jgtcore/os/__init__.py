"""
OS utilities module for jgtcore

This module contains OS-related functions migrated from jgtutils:
- TLID (Time/Location ID) range utilities
- Instrument and timeframe conversion
- File path and filename utilities
- Directory management helpers

Provides comprehensive OS and file system utilities for JGT applications.
"""

from .helpers import (
    # TLID range functions
    tlid_range_to_start_end_datetime,
    tlid_range_to_jgtfxcon_start_end_str,
    tlid_dt_to_string,
    tlidmin_to_dt,
    
    # Instrument/timeframe conversion
    i2fn, fn2i, t2fn, fn2t,
    topovfn, fn2pov,
    
    # Advanced TLID calculation
    get_dt_format_pattern,
    calculate_start_datetime,
    calculate_tlid_range,
    
    # File naming utilities
    mk_fn_range,
    ensure_directory_exists,
    
    # Constants
    HAS_TLID,
    HAS_DATEUTIL,
)

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