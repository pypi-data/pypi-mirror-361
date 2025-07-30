"""
CLI utilities module for jgtcore

This module contains CLI-related functions migrated from jgtutils:
- Argument parsing and handling (common.py)
- CLI helper functions (helper.py)
- Command-line interface utilities

Provides comprehensive CLI support with settings integration,
JSON output formatting, and graceful signal handling.
"""

from .common import (
    new_parser,
    parse_args,
    add_settings_argument,
    load_arg_default_from_settings,
    load_arg_default_from_settings_if_exist,
    get_parsed_args,
    get_current_settings,
    SETTING_ARGNAME,
    SETTING_ARGNAME_ALIAS,
)

from .helper import (
    print_jsonl_message,
    build_jsonl_message,
    signal_handler,
    add_exiting_quietly,
    print_error_message,
    print_success_message,
    print_warning_message,
    print_info_message,
    printl,  # Legacy alias
)

__all__ = [
    # Common CLI functions
    'new_parser',
    'parse_args',
    'add_settings_argument',
    'load_arg_default_from_settings',
    'load_arg_default_from_settings_if_exist',
    'get_parsed_args',
    'get_current_settings',
    'SETTING_ARGNAME',
    'SETTING_ARGNAME_ALIAS',
    
    # Helper functions
    'print_jsonl_message',
    'build_jsonl_message',
    'signal_handler',
    'add_exiting_quietly',
    'print_error_message',
    'print_success_message',
    'print_warning_message',
    'print_info_message',
    'printl',
]