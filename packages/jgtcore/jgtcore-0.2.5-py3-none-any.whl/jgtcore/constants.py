"""
Constants module for jgtcore

Trading and data processing constants migrated from jgtutils.
Provides consistent constant definitions across the JGT ecosystem.
"""

# Default data processing constants
NB_BARS_BY_DEFAULT_IN_CDS = 1000

# Column name constants for trading data
OPEN = "open"
HIGH = "high"
LOW = "low"
CLOSE = "close"
VOLUME = "volume"
DATE = "date"
TIME = "time"

# Alligator indicator constants
JAW = "jaw"
TEETH = "teeth"
LIPS = "lips"

# Bill Williams Alligator constants
BJAW = "bjaw"
BTEETH = "bteeth"
BLIPS = "blips"

# TAlligator constants
TJAW = "tjaw"
TTEETH = "tteeth"
TLIPS = "tlips"

# Awesome Oscillator constants
AO = "ao"
AC = "ac"
indicator_AO_awesomeOscillator_column_name = AO  # Legacy alias for compatibility

# Fractal constants
FH = "fh"
FL = "fl"
FH3 = "fh3"
FL3 = "fl3"
FH5 = "fh5"
FL5 = "fl5"

# MFI (Money Flow Index) constants
MFI = "mfi"
MFI_SQUAT = "mfi_squat"
MFI_GREEN = "mfi_green"
MFI_FADE = "mfi_fade"
MFI_FAKE = "mfi_fake"

# FDB (Fractal Divergence Bar) constants
FDB = "fdb"
FDBB = "fdbb"
FDBS = "fdbs"
FDB_TARGET = "fdb_target"

# Zone signal constants
ZONE_SIGNAL = "zone_signal"

# Vector constants for ML
VECTOR_AO_FDBS = "vector_ao_fdbs"
VECTOR_AO_FDBB = "vector_ao_fdbb"

# IDS columns for normalization
IDS_COLUMNS_TO_NORMALIZE = [
    AO, AC, MFI, FH, FL, FH3, FL3, FH5, FL5,
    JAW, TEETH, LIPS, BJAW, BTEETH, BLIPS, TJAW, TTEETH, TLIPS
]

# ML default columns to keep
ML_DEFAULT_COLUMNS_TO_KEEP = [
    OPEN, HIGH, LOW, CLOSE, VOLUME, DATE,
    JAW, TEETH, LIPS, AO, AC, MFI,
    FH, FL, FDBB, FDBS, ZONE_SIGNAL
]

#must be name like that for compatibiltiy
# List of columns to remove
columns_to_remove = ['aofvalue', 'aofhighao', 'aoflowao', 'aofhigh', 'aoflow', 'aocolor', 'accolor','fdbbhigh','fdbblow','fdbshigh','fdbslow']




# Chart configuration constants
DEFAULT_CHART_WIDTH = 1200
DEFAULT_CHART_HEIGHT = 800

# Data processing constants
DEFAULT_TIMEFRAME = "H1"
DEFAULT_INSTRUMENT = "EUR/USD"

# File operation constants
DEFAULT_DATA_DIR = "data"
CURRENT_DATA_DIR = "current"
CACHE_DATA_DIR = "cache"

# Export constants
DEFAULT_EXPORT_FORMAT = "csv"
SUPPORTED_EXPORT_FORMATS = ["csv", "json", "yaml", "xlsx"]

__all__ = [
    # Default processing constants
    'NB_BARS_BY_DEFAULT_IN_CDS',
    
    # Column names
    'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'DATE', 'TIME',
    
    # Alligator constants
    'JAW', 'TEETH', 'LIPS', 'BJAW', 'BTEETH', 'BLIPS', 'TJAW', 'TTEETH', 'TLIPS',
    
    # Oscillator constants
    'AO', 'AC', 'indicator_AO_awesomeOscillator_column_name',
    
    # Fractal constants
    'FH', 'FL', 'FH3', 'FL3', 'FH5', 'FL5',
    
    # MFI constants
    'MFI', 'MFI_SQUAT', 'MFI_GREEN', 'MFI_FADE', 'MFI_FAKE',
    
    # FDB constants
    'FDB', 'FDBB', 'FDBS', 'FDB_TARGET',
    
    # Signal constants
    'ZONE_SIGNAL',
    
    # Vector constants
    'VECTOR_AO_FDBS', 'VECTOR_AO_FDBB',
    
    # Column lists
    'IDS_COLUMNS_TO_NORMALIZE', 'ML_DEFAULT_COLUMNS_TO_KEEP',
    
    # Chart constants
    'DEFAULT_CHART_WIDTH', 'DEFAULT_CHART_HEIGHT',
    
    # Processing constants
    'DEFAULT_TIMEFRAME', 'DEFAULT_INSTRUMENT',
    
    # File constants
    'DEFAULT_DATA_DIR', 'CURRENT_DATA_DIR', 'CACHE_DATA_DIR',
    
    # Export constants
    'DEFAULT_EXPORT_FORMAT', 'SUPPORTED_EXPORT_FORMATS',
]
