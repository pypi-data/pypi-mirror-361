"""
Environment management module for jgtcore

This module contains environment-related functions migrated from jgtutils:
- Environment variable loading and management (.env files)
- JGT-specific environment setup (.jgt/env.sh, .env.jgtset, .env.fxtrade)
- YAML configuration loading
- Multi-source environment loading with fallbacks

Provides comprehensive environment management for JGT applications.
"""

from .loaders import (
    # FX trade environment
    get_dotfxtrade_env_path,
    load_dotfxtrade_env,
    is_dotfxtrade_env_exists,
    
    # JGT environment shell
    get_dotjgt_env_sh_path,
    load_dotjgt_env_sh,
    is_dotjgt_env_sh_exists,
    
    # JGT set exported environment
    get_dotenv_jgtset_export_path,
    load_dotjgtset_exported_env,
    
    # YAML environment
    load_jgtyaml_env,
    
    # Comprehensive loading
    load_env,
    
    # Utilities
    get_openai_key,
    load_arg_from_jgt_env,
    
    # Constants
    JGT_SUBDIR_NAME,
    JGT_ENV_EXPORT_NAME,
    JGT_FXTRADE_ENV_FILENAME,
    HAS_DOTENV,
    HAS_YAML,
)

__all__ = [
    # FX trade environment
    'get_dotfxtrade_env_path',
    'load_dotfxtrade_env',
    'is_dotfxtrade_env_exists',
    
    # JGT environment shell
    'get_dotjgt_env_sh_path',
    'load_dotjgt_env_sh',
    'is_dotjgt_env_sh_exists',
    
    # JGT set exported environment
    'get_dotenv_jgtset_export_path',
    'load_dotjgtset_exported_env',
    
    # YAML environment
    'load_jgtyaml_env',
    
    # Comprehensive loading
    'load_env',
    
    # Utilities
    'get_openai_key',
    'load_arg_from_jgt_env',
    
    # Constants
    'JGT_SUBDIR_NAME',
    'JGT_ENV_EXPORT_NAME',
    'JGT_FXTRADE_ENV_FILENAME',
    'HAS_DOTENV',
    'HAS_YAML',
]