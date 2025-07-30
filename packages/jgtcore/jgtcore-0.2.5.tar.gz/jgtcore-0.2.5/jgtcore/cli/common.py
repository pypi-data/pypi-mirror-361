"""
CLI common utilities for jgtcore

Core argument parsing and CLI functionality migrated from jgtutils.
Provides argument parser creation, settings integration, and post-processing.
"""

import argparse
import json
import os
import sys
from typing import Optional

# Optional YAML support - graceful fallback to JSON-only if not available
try:
    import ruamel.yaml
    yaml = ruamel.yaml.YAML()
    HAS_YAML = True
except ImportError:
    yaml = None
    HAS_YAML = False

# Import core functions from jgtcore
from ..core import load_settings, get_settings, update_settings

# CLI constants
SETTING_ARGNAME = 'settings'
SETTING_ARGNAME_ALIAS = 'ls'

# Global variables for parser state
default_parser = None
args = None
settings = None


def new_parser(description: str, epilog: str = None, prog: str = None,
               enable_specified_settings: bool = True,
               add_exiting_quietly_flag: bool = False,
               exiting_quietly_message: str = None,
               exiting_quietly_handler=None) -> argparse.ArgumentParser:
    """
    Create a new argument parser with JGT-specific enhancements.
    
    Args:
        description: Parser description
        epilog: Epilog text  
        prog: Program name
        enable_specified_settings: Enable --settings argument
        add_exiting_quietly_flag: Add signal handling for graceful exit
        exiting_quietly_message: Message to show on graceful exit
        exiting_quietly_handler: Handler function for graceful exit
        
    Returns:
        Configured ArgumentParser instance
    """
    global default_parser
    
    if add_exiting_quietly_flag or exiting_quietly_handler is not None:
        from .helper import add_exiting_quietly
        add_exiting_quietly(exiting_quietly_message, exiting_quietly_handler)
        
    default_parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        prog=prog
    )
    
    if enable_specified_settings:
        default_parser = add_settings_argument(default_parser)
        if '--help' not in sys.argv:
            default_parser = _preload_settings_from_args(default_parser)
    
    return default_parser


def parse_args(parser: Optional[argparse.ArgumentParser] = None) -> argparse.Namespace:
    """
    Parse command line arguments with JGT-specific post-processing.
    
    Args:
        parser: ArgumentParser instance (uses default if None)
        
    Returns:
        Parsed arguments namespace with JGT enhancements
    """
    global default_parser, args, settings
    
    if parser is None:
        parser = default_parser
    
    args = parser.parse_args()
    
    try:
        # Set jgtcommon_settings in the args to store settings
        setattr(args, 'jgtcommon_settings', get_settings())
    except:
        pass
    
    args = _post_parse_dependent_arguments_rules()
    return args


def add_settings_argument(parser: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    """
    Add --settings argument to parser for custom settings file.
    
    Args:
        parser: ArgumentParser instance (uses default if None)
        
    Returns:
        Parser with settings argument added
    """
    global default_parser
    
    if parser is None:
        parser = default_parser
    
    try:
        parser.add_argument(
            f'-{SETTING_ARGNAME_ALIAS}', f'--{SETTING_ARGNAME}',
            type=str,
            help='Load settings from a specific settings file (overrides default settings '
                 '(/etc/jgt/settings.json and HOME/.jgt/settings.json and .jgt/settings.json)).',
            required=False
        )
    except argparse.ArgumentError as e:
        # Handle conflicting option strings gracefully
        if 'conflicting option strings' not in str(e):
            raise e
    
    return parser


def _preload_settings_from_args(parser: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    """
    Pre-load settings from arguments before full parsing.
    
    Args:
        parser: ArgumentParser instance (uses default if None)
        
    Returns:
        Parser after settings pre-loading
    """
    global default_parser, settings
    
    if parser is None:
        parser = default_parser
    
    args_partial, unknown = parser.parse_known_args()
    custom_path = getattr(args_partial, SETTING_ARGNAME, None)
    settings = load_settings(custom_path)
    
    return parser


def load_arg_default_from_settings(argname: str, default_value,
                                  alias: str = None,
                                  from_jgt_env: bool = False,
                                  exclude_env_alias: bool = False):
    """
    Load argument default value from settings.
    
    Args:
        argname: Argument name to look up
        default_value: Default value if not found
        alias: Alternative argument name to try
        from_jgt_env: Whether to load from JGT environment
        exclude_env_alias: Whether to exclude alias from env lookup
        
    Returns:
        Value from settings or default
    """
    global settings
    
    if settings is None or len(settings) == 0:
        settings = load_settings()
    
    value = settings.get(argname, default_value)
    if alias is not None and value == default_value:
        value = settings.get(alias, default_value)
    
    if from_jgt_env:
        from ..env import load_arg_from_jgt_env
        _alias = None if exclude_env_alias else alias
        env_value = load_arg_from_jgt_env(argname, _alias)
        if env_value is not None:
            value = env_value
    
    return value


def load_arg_default_from_settings_if_exist(argname: str, default_value,
                                          alias: str = None,
                                          from_jgt_env: bool = False,
                                          exclude_env_alias: bool = False):
    """
    Load argument default from settings only if settings exist.
    
    Args:
        argname: Argument name to look up
        default_value: Default value if not found
        alias: Alternative argument name to try
        from_jgt_env: Whether to load from JGT environment
        exclude_env_alias: Whether to exclude alias from env lookup
        
    Returns:
        Value from settings or default
    """
    try:
        return load_arg_default_from_settings(
            argname, default_value, alias, from_jgt_env, exclude_env_alias
        )
    except:
        return default_value


def _post_parse_dependent_arguments_rules() -> argparse.Namespace:
    """
    Apply post-parsing rules for dependent arguments.
    
    Returns:
        Args namespace with post-processing applied
    """
    global args
    
    _check_if_parsed()
    
    # Apply various post-processing rules
    args = _quiet_post_parse()
    
    # Convert instrument and timeframe strings if needed
    try:
        if hasattr(args, "instrument") and args.instrument and isinstance(args.instrument, str):
            from ..os import fn2i
            setattr(args, 'instrument', fn2i(args.instrument))
    except:
        pass
    
    try:
        if hasattr(args, "timeframe") and args.timeframe and isinstance(args.timeframe, str):
            from ..os import fn2t
            setattr(args, 'timeframe', fn2t(args.timeframe))
    except:
        pass
    
    # Additional post-processing can be added here as needed
    # This is a simplified version - the full version has many more rules
    
    return args


def _check_if_parsed():
    """Check if arguments have been parsed."""
    global args
    if args is None:
        raise RuntimeError("Arguments not parsed yet. Call parse_args() first.")


def _quiet_post_parse() -> argparse.Namespace:
    """Handle quiet flag post-processing."""
    global args
    
    # Set quiet attribute based on verbose level if not already set
    try:
        if not hasattr(args, 'quiet') and (hasattr(args, 'verbose') and args.verbose == 0):
            # Add quiet to args - quiet mode activated when verbose level is 0
            setattr(args, 'quiet', True)
        elif not hasattr(args, 'quiet'):
            setattr(args, 'quiet', False)
    except:
        # Fallback - ensure quiet attribute exists
        if not hasattr(args, 'quiet'):
            setattr(args, 'quiet', False)
    
    return args


def get_parsed_args() -> Optional[argparse.Namespace]:
    """
    Get the currently parsed arguments.
    
    Returns:
        Parsed arguments namespace or None if not parsed yet
    """
    global args
    return args


def get_current_settings() -> Optional[dict]:
    """
    Get the currently loaded settings.
    
    Returns:
        Settings dictionary or None if not loaded
    """
    global settings
    return settings


__all__ = [
    'new_parser',
    'parse_args', 
    'add_settings_argument',
    'load_arg_default_from_settings',
    'load_arg_default_from_settings_if_exist',
    'get_parsed_args',
    'get_current_settings',
    'SETTING_ARGNAME',
    'SETTING_ARGNAME_ALIAS',
]