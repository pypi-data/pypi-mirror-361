"""
Backward compatibility layer for jgtutils migration

This module provides compatibility imports to ensure existing code
that imports from jgtutils continues to work during and after migration.

Usage:
    # Legacy jgtutils imports will be redirected through this layer
    from jgtutils import get_config  # -> jgtcore.get_config
    from jgtutils.jgtcommon import new_parser  # -> jgtcore.cli.new_parser
    
The migration will happen in phases:
1. Core functions (already done) - config, settings, timeframe
2. CLI utilities - argument parsing, helpers
3. OS utilities - path helpers, TLID ranges, WSL
4. Environment utilities - env loading, setup
5. FX utilities - transaction handling, trading helpers
6. Logging utilities
"""

# Phase 1: Core functions (already available in jgtcore)
from .core import (
    get_config,
    get_setting,
    setup_environment,
    get_config_value,
    is_demo_mode,
    readconfig,
    load_settings,
    get_settings,
    dt_from_last_week_as_datetime,
    dt_from_last_week_as_string_fxformat,
)

from .timeframe import (
    get_current_time,
    get_times_by_timeframe_str,
    is_timeframe_reached,
    simulate_timeframe_reached,
    TimeframeChecker,
)

# Phase 2-6: Future migration placeholders
# These will be uncommented as modules are migrated

# Phase 2: CLI utilities - COMPLETED
from .cli import (
    new_parser, parse_args, print_jsonl_message, add_settings_argument,
    load_arg_default_from_settings, load_arg_default_from_settings_if_exist,
    printl  # Legacy alias
)

# Phase 3: OS utilities - COMPLETED
from .os import (
    tlid_range_to_jgtfxcon_start_end_str, tlid_range_to_start_end_datetime,
    tlid_dt_to_string, tlidmin_to_dt, i2fn, fn2i, t2fn, fn2t,
    topovfn, fn2pov, calculate_tlid_range, mk_fn_range, ensure_directory_exists
)

# Phase 4: Environment utilities - COMPLETED
from .env import (
    load_dotjgt_env_sh, load_dotjgtset_exported_env, load_dotfxtrade_env, load_env,
    load_arg_from_jgt_env, get_openai_key, load_jgtyaml_env
)

# Phase 5: FX utilities - COMPLETED
from .fx import (
    FXTransactDataHelper, FXTransactWrapper, FXTrade, FXTrades, FXOrder, FXOrders,
    ftdh, ftw, sanitize_filename
)

# Phase 6: Logging utilities - COMPLETED
from .logging import (
    get_logger, setup_logging, add_error_handler, set_log_level, write_log,
    info, warning, error, critical, debug, exception
)

# Constants - COMPLETED
from .constants import (
    NB_BARS_BY_DEFAULT_IN_CDS, OPEN, HIGH, LOW, CLOSE, VOLUME, DATE, TIME,
    JAW, TEETH, LIPS, BJAW, BTEETH, BLIPS, TJAW, TTEETH, TLIPS,
    AO, AC, FH, FL, FH3, FL3, FH5, FL5,
    MFI, MFI_SQUAT, MFI_GREEN, MFI_FADE, MFI_FAKE,
    FDB, FDBB, FDBS, FDB_TARGET, ZONE_SIGNAL,
    VECTOR_AO_FDBS, VECTOR_AO_FDBB,
    IDS_COLUMNS_TO_NORMALIZE, ML_DEFAULT_COLUMNS_TO_KEEP
)

# Compatibility mappings for renamed/moved functions
COMPATIBILITY_MAP = {
    # Core functions maintain same names
    'get_config': get_config,
    'get_setting': get_setting,
    'setup_environment': setup_environment,
    'get_config_value': get_config_value,
    'is_demo_mode': is_demo_mode,
    'readconfig': readconfig,
    'load_settings': load_settings,
    'get_settings': get_settings,
    'dt_from_last_week': dt_from_last_week_as_string_fxformat,  # Alias mapping
    
    # Timeframe functions
    'get_current_time': get_current_time,
    'get_times_by_timeframe_str': get_times_by_timeframe_str,
    'is_timeframe_reached': is_timeframe_reached,
    'simulate_timeframe_reached': simulate_timeframe_reached,
    'TimeframeChecker': TimeframeChecker,
    
    # CLI functions - Phase 2
    'new_parser': new_parser,
    'parse_args': parse_args,
    'print_jsonl_message': print_jsonl_message,
    'printl': printl,
    'add_settings_argument': add_settings_argument,
    'load_arg_default_from_settings': load_arg_default_from_settings,
    'load_arg_default_from_settings_if_exist': load_arg_default_from_settings_if_exist,
    
    # OS functions - Phase 3
    'tlid_range_to_jgtfxcon_start_end_str': tlid_range_to_jgtfxcon_start_end_str,
    'tlid_range_to_start_end_datetime': tlid_range_to_start_end_datetime,
    'tlid_dt_to_string': tlid_dt_to_string,
    'tlidmin_to_dt': tlidmin_to_dt,
    'i2fn': i2fn,
    'fn2i': fn2i,
    't2fn': t2fn,
    'fn2t': fn2t,
    'topovfn': topovfn,
    'fn2pov': fn2pov,
    'calculate_tlid_range': calculate_tlid_range,
    'mk_fn_range': mk_fn_range,
    'ensure_directory_exists': ensure_directory_exists,
    
    # Environment functions - Phase 4
    'load_dotjgt_env_sh': load_dotjgt_env_sh,
    'load_dotjgtset_exported_env': load_dotjgtset_exported_env,
    'load_dotfxtrade_env': load_dotfxtrade_env,
    'load_env': load_env,
    'load_arg_from_jgt_env': load_arg_from_jgt_env,
    'get_openai_key': get_openai_key,
    'load_jgtyaml_env': load_jgtyaml_env,
    
    # FX functions - Phase 5
    'FXTransactDataHelper': FXTransactDataHelper,
    'FXTransactWrapper': FXTransactWrapper,
    'FXTrade': FXTrade,
    'FXTrades': FXTrades,
    'FXOrder': FXOrder,
    'FXOrders': FXOrders,
    'ftdh': ftdh,
    'ftw': ftw,
    'sanitize_filename': sanitize_filename,
    
    # Logging functions - Phase 6
    'get_logger': get_logger,
    'setup_logging': setup_logging,
    'add_error_handler': add_error_handler,
    'set_log_level': set_log_level,
    'write_log': write_log,
    'info': info,
    'warning': warning,
    'error': error,
    'critical': critical,
    'debug': debug,
    'exception': exception,
    
    # Constants - Phase 7
    'NB_BARS_BY_DEFAULT_IN_CDS': NB_BARS_BY_DEFAULT_IN_CDS,
    'OPEN': OPEN,
    'HIGH': HIGH,
    'LOW': LOW,
    'CLOSE': CLOSE,
    'VOLUME': VOLUME,
    'DATE': DATE,
    'TIME': TIME,
    'JAW': JAW,
    'TEETH': TEETH,
    'LIPS': LIPS,
    'BJAW': BJAW,
    'BTEETH': BTEETH,
    'BLIPS': BLIPS,
    'TJAW': TJAW,
    'TTEETH': TTEETH,
    'TLIPS': TLIPS,
    'AO': AO,
    'AC': AC,
    'FH': FH,
    'FL': FL,
    'FH3': FH3,
    'FL3': FL3,
    'FH5': FH5,
    'FL5': FL5,
    'MFI': MFI,
    'MFI_SQUAT': MFI_SQUAT,
    'MFI_GREEN': MFI_GREEN,
    'MFI_FADE': MFI_FADE,
    'MFI_FAKE': MFI_FAKE,
    'FDB': FDB,
    'FDBB': FDBB,
    'FDBS': FDBS,
    'FDB_TARGET': FDB_TARGET,
    'ZONE_SIGNAL': ZONE_SIGNAL,
    'VECTOR_AO_FDBS': VECTOR_AO_FDBS,
    'VECTOR_AO_FDBB': VECTOR_AO_FDBB,
    'IDS_COLUMNS_TO_NORMALIZE': IDS_COLUMNS_TO_NORMALIZE,
    'ML_DEFAULT_COLUMNS_TO_KEEP': ML_DEFAULT_COLUMNS_TO_KEEP,
}

def get_compatible_function(name):
    """
    Get a function by its jgtutils name for compatibility.
    
    Args:
        name (str): The function name as used in jgtutils
        
    Returns:
        callable: The corresponding jgtcore function
        
    Raises:
        AttributeError: If the function is not available or not yet migrated
    """
    if name in COMPATIBILITY_MAP:
        return COMPATIBILITY_MAP[name]
    
    raise AttributeError(f"Function '{name}' not available in jgtcore compatibility layer. "
                        f"It may not be migrated yet or may have been renamed.")

__all__ = [
    # Core functions
    'get_config', 'get_setting', 'setup_environment', 'get_config_value', 'is_demo_mode',
    'readconfig', 'load_settings', 'get_settings',
    'dt_from_last_week_as_datetime', 'dt_from_last_week_as_string_fxformat',
    
    # Timeframe functions
    'get_current_time', 'get_times_by_timeframe_str', 'is_timeframe_reached',
    'simulate_timeframe_reached', 'TimeframeChecker',
    
    # CLI functions - Phase 2
    'new_parser', 'parse_args', 'print_jsonl_message', 'printl',
    'add_settings_argument', 'load_arg_default_from_settings',
    'load_arg_default_from_settings_if_exist',
    
    # OS functions - Phase 3
    'tlid_range_to_jgtfxcon_start_end_str', 'tlid_range_to_start_end_datetime',
    'tlid_dt_to_string', 'tlidmin_to_dt', 'i2fn', 'fn2i', 't2fn', 'fn2t',
    'topovfn', 'fn2pov', 'calculate_tlid_range', 'mk_fn_range', 'ensure_directory_exists',
    
    # Environment functions - Phase 4
    'load_dotjgt_env_sh', 'load_dotjgtset_exported_env', 'load_dotfxtrade_env', 'load_env',
    'load_arg_from_jgt_env', 'get_openai_key', 'load_jgtyaml_env',
    
    # FX functions - Phase 5
    'FXTransactDataHelper', 'FXTransactWrapper', 'FXTrade', 'FXTrades', 
    'FXOrder', 'FXOrders', 'ftdh', 'ftw', 'sanitize_filename',
    
    # Logging functions - Phase 6
    'get_logger', 'setup_logging', 'add_error_handler', 'set_log_level', 'write_log',
    'info', 'warning', 'error', 'critical', 'debug', 'exception',
    
    # Constants - Phase 7
    'NB_BARS_BY_DEFAULT_IN_CDS', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'DATE', 'TIME',
    'JAW', 'TEETH', 'LIPS', 'BJAW', 'BTEETH', 'BLIPS', 'TJAW', 'TTEETH', 'TLIPS',
    'AO', 'AC', 'FH', 'FL', 'FH3', 'FL3', 'FH5', 'FL5',
    'MFI', 'MFI_SQUAT', 'MFI_GREEN', 'MFI_FADE', 'MFI_FAKE',
    'FDB', 'FDBB', 'FDBS', 'FDB_TARGET', 'ZONE_SIGNAL',
    'VECTOR_AO_FDBS', 'VECTOR_AO_FDBB', 'IDS_COLUMNS_TO_NORMALIZE', 'ML_DEFAULT_COLUMNS_TO_KEEP',
    
    # Compatibility utilities
    'COMPATIBILITY_MAP', 'get_compatible_function',
]