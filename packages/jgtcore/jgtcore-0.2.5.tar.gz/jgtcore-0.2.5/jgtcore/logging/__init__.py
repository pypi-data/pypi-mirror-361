"""
Logging utilities module for jgtcore

This module contains logging-related functions migrated from jgtutils:
- JGT-specific logging configuration and setup
- Log formatting and handling utilities
- Convenience logging functions (info, warning, error, etc.)
- Error handler management

Provides comprehensive logging capabilities for JGT applications.
"""

from .jgtlogging import (
    # Core functions
    get_logger,
    setup_logging,
    add_error_handler,
    set_log_level,
    write_log,
    
    # Convenience functions
    info,
    warning, 
    error,
    critical,
    debug,
    exception,
    
    # Constants
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOGGER_NAME,
    DEFAULT_LOG_FORMAT,
    DEFAULT_DATE_FORMAT,
    SIMPLE_LOG_FORMAT,
)

__all__ = [
    # Core functions
    'get_logger',
    'setup_logging',
    'add_error_handler',
    'set_log_level',
    'write_log',
    
    # Convenience functions
    'info',
    'warning', 
    'error',
    'critical',
    'debug',
    'exception',
    
    # Constants
    'DEFAULT_LOG_LEVEL',
    'DEFAULT_LOGGER_NAME',
    'DEFAULT_LOG_FORMAT',
    'DEFAULT_DATE_FORMAT',
    'SIMPLE_LOG_FORMAT',
]