"""
JGT logging utilities for jgtcore

Logging configuration and utilities migrated from jgtutils.
Provides JGT-specific logging setup and convenience functions.
"""

import logging
import sys
import traceback
import os
from typing import Optional


# Default configuration
DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_LOGGER_NAME = "jgtcore"
DEFAULT_LOG_FORMAT = "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s"
DEFAULT_DATE_FORMAT = "%Y.%m.%d %H:%M:%S"
SIMPLE_LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

# Global logger state
_logger = None
_console_handler = None
_error_handler = None
_log_level = DEFAULT_LOG_LEVEL
_logger_name = DEFAULT_LOGGER_NAME


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get or create a JGT logger instance.
    
    Args:
        name: Logger name (uses default if None)
        
    Returns:
        Configured logger instance
    """
    global _logger, _logger_name
    
    if name is None:
        name = _logger_name
    
    if _logger is None or _logger.name != name:
        _logger = logging.getLogger(name)
        _logger_name = name
    
    return _logger


def setup_logging(log_file: Optional[str] = None, 
                 console_level: Optional[int] = None,
                 file_level: int = logging.INFO,
                 logger_name: Optional[str] = None,
                 log_format: Optional[str] = None,
                 date_format: Optional[str] = None) -> logging.Logger:
    """
    Set up JGT logging configuration.
    
    Args:
        log_file: Log file path (auto-generated if None)
        console_level: Console logging level (uses default if None)
        file_level: File logging level
        logger_name: Logger name (uses default if None)
        log_format: Log format string (uses default if None)
        date_format: Date format string (uses default if None)
        
    Returns:
        Configured logger instance
    """
    global _logger, _console_handler, _log_level, _logger_name
    
    if logger_name:
        _logger_name = logger_name
    
    if console_level is not None:
        _log_level = console_level
    
    if log_format is None:
        log_format = DEFAULT_LOG_FORMAT
    
    if date_format is None:
        date_format = DEFAULT_DATE_FORMAT
    
    # Generate log file name if not provided
    if log_file is None:
        try:
            import __main__
            if hasattr(__main__, '__file__') and __main__.__file__:
                log_file = f"{os.path.splitext(os.path.basename(__main__.__file__))[0]}.log"
            else:
                log_file = "jgtcore.log"
        except:
            log_file = "jgtcore.log"
    
    try:
        # Create formatter
        formatter = logging.Formatter(log_format, datefmt=date_format)
        
        # Set up basic configuration for file logging
        logging.basicConfig(
            filename=log_file,
            level=file_level,
            format=log_format,
            datefmt=date_format,
            filemode='a'
        )
        
        # Get logger
        _logger = get_logger(_logger_name)
        _logger.setLevel(min(_log_level, file_level))
        
        # Add console handler if not already present
        if not any(isinstance(h, logging.StreamHandler) and h.stream == sys.stdout 
                  for h in _logger.handlers):
            _console_handler = logging.StreamHandler(sys.stdout)
            _console_handler.setLevel(_log_level)
            _console_handler.setFormatter(formatter)
            _logger.addHandler(_console_handler)
        
        return _logger
        
    except Exception as e:
        print(f"Exception during logging setup: {e}\n{traceback.format_exc()}")
        print("Logging setup failed - continuing with basic logger")
        _logger = get_logger(_logger_name)
        return _logger


def add_error_handler(error_file: str = "error.log") -> bool:
    """
    Add error file handler to logger.
    
    Args:
        error_file: Error log file path
        
    Returns:
        True if successful, False otherwise
    """
    global _logger, _error_handler
    
    try:
        if _logger is None:
            _logger = get_logger()
        
        # Check if error handler already exists
        if not any(isinstance(h, logging.FileHandler) and h.baseFilename.endswith(error_file)
                  for h in _logger.handlers):
            _error_handler = logging.FileHandler(error_file)
            _error_handler.setLevel(logging.ERROR)
            
            formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT)
            _error_handler.setFormatter(formatter)
            
            _logger.addHandler(_error_handler)
        
        return True
        
    except Exception as e:
        print(f"Failed to add error handler: {e}")
        return False


def set_log_level(level: str = "WARNING", logger_name: Optional[str] = None) -> bool:
    """
    Set logging level for JGT logger.
    
    Args:
        level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Logger name (uses current if None)
        
    Returns:
        True if successful, False otherwise
    """
    global _log_level, _logger
    
    try:
        numeric_level = getattr(logging, level.upper())
        _log_level = numeric_level
        
        if logger_name:
            _logger = get_logger(logger_name)
        elif _logger is None:
            _logger = get_logger()
        
        _logger.setLevel(_log_level)
        
        # Update console handler level if it exists
        if _console_handler:
            _console_handler.setLevel(_log_level)
        
        _logger.info(f"Log level set to {level.upper()} ({numeric_level})")
        return True
        
    except (AttributeError, ValueError) as e:
        print(f"Invalid log level '{level}': {e}")
        return False


def write_log(msg: str, level: str = "INFO") -> bool:
    """
    Write log message at specified level.
    
    Args:
        msg: Log message
        level: Log level name
        
    Returns:
        True if successful, False otherwise
    """
    global _logger
    
    try:
        if _logger is None:
            _logger = get_logger()
        
        numeric_level = getattr(logging, level.upper())
        
        if numeric_level >= _log_level:
            _logger.log(numeric_level, msg)
        
        return True
        
    except (AttributeError, ValueError) as e:
        print(f"Error writing log: {e}")
        return False


# Convenience logging functions

def info(msg: str, *args):
    """Log info message."""
    if _logger is None:
        setup_logging()
    _logger.info(msg, *args)


def warning(msg: str, *args):
    """Log warning message."""
    if _logger is None:
        setup_logging()
    _logger.warning(msg, *args)


def error(msg: str, *args):
    """Log error message."""
    if _logger is None:
        setup_logging()
    _logger.error(msg, *args)


def critical(msg: str, *args):
    """Log critical message."""
    if _logger is None:
        setup_logging()
    _logger.critical(msg, *args)


def debug(msg: str, *args):
    """Log debug message."""
    if _logger is None:
        setup_logging()
    _logger.debug(msg, *args)


def exception(msg: str, *args):
    """Log exception with traceback."""
    if _logger is None:
        setup_logging()
    _logger.exception(msg, *args)


# Initialize basic logger on import
try:
    _logger = get_logger()
except Exception:
    print("Failed to create initial logger object")


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