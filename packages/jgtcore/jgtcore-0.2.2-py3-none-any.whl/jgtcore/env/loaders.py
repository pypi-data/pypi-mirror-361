"""
Environment loaders for jgtcore

Environment management functions migrated from jgtutils.
Handles loading environment variables from various sources including
.env files, JGT-specific configurations, and YAML config files.
"""

import os
from typing import Optional, Dict, Any

# Required for .env file loading
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    load_dotenv = None
    HAS_DOTENV = False

# Optional YAML support - graceful fallback to JSON-only if not available
try:
    from ruamel.yaml import YAML
    yaml = YAML()
    HAS_YAML = True
except ImportError:
    yaml = None
    HAS_YAML = False

# JGT Environment constants
JGT_SUBDIR_NAME = ".jgt"
JGT_ENV_EXPORT_NAME = ".env.jgtset"
JGT_FXTRADE_ENV_FILENAME = ".env.fxtrade"


# FX Trade Environment Functions

def get_dotfxtrade_env_path() -> str:
    """
    Get path to FX trade environment file.
    
    Returns:
        Path to .env.fxtrade file in current directory
    """
    return os.path.join(os.getcwd(), JGT_FXTRADE_ENV_FILENAME)


def load_dotfxtrade_env() -> bool:
    """
    Load FX trade environment variables from .env.fxtrade file.
    
    Returns:
        True if file exists and was loaded, False otherwise
        
    Raises:
        ImportError: If python-dotenv is not available
    """
    if not HAS_DOTENV:
        raise ImportError("python-dotenv is required for load_dotfxtrade_env function")
    
    dotfxtrade_env_path = get_dotfxtrade_env_path()
    if os.path.exists(dotfxtrade_env_path):
        load_dotenv(dotenv_path=dotfxtrade_env_path)
        return True
    else:
        return False


def is_dotfxtrade_env_exists() -> bool:
    """
    Check if FX trade environment file exists.
    
    Returns:
        True if .env.fxtrade exists, False otherwise
    """
    return os.path.exists(get_dotfxtrade_env_path())


# JGT Environment Shell Functions

def get_dotjgt_env_sh_path() -> str:
    """
    Get path to JGT environment shell file.
    
    Returns:
        Path to .jgt/env.sh file in current directory
    """
    return os.path.join(os.getcwd(), JGT_SUBDIR_NAME, "env.sh")


def load_dotjgt_env_sh() -> bool:
    """
    Load JGT environment variables from .jgt/env.sh file.
    
    Returns:
        True if file exists and was loaded, False otherwise
        
    Raises:
        ImportError: If python-dotenv is not available
    """
    if not HAS_DOTENV:
        raise ImportError("python-dotenv is required for load_dotjgt_env_sh function")
    
    dotjgt_env_sh_path = get_dotjgt_env_sh_path()
    if os.path.exists(dotjgt_env_sh_path):
        load_dotenv(dotenv_path=dotjgt_env_sh_path)
        return True
    else:
        return False


def is_dotjgt_env_sh_exists() -> bool:
    """
    Check if JGT environment shell file exists.
    
    Returns:
        True if .jgt/env.sh exists, False otherwise
    """
    return os.path.exists(get_dotjgt_env_sh_path())


# JGT Set Exported Environment Functions

def get_dotenv_jgtset_export_path(in_jgt_subdir: bool = False) -> str:
    """
    Get path to JGT set exported environment file.
    
    Args:
        in_jgt_subdir: Whether to place file in .jgt subdirectory
        
    Returns:
        Path to .env.jgtset file
    """
    if in_jgt_subdir:
        jgt_export_directory = os.path.join(os.getcwd(), JGT_SUBDIR_NAME)
        os.makedirs(jgt_export_directory, exist_ok=True)
    else:
        jgt_export_directory = os.getcwd()
        
    batch_file_path = os.path.join(jgt_export_directory, JGT_ENV_EXPORT_NAME)
    return batch_file_path


def load_dotjgtset_exported_env() -> bool:
    """
    Load JGT set exported environment variables.
    
    Returns:
        True if file exists and was loaded, False otherwise
        
    Raises:
        ImportError: If python-dotenv is not available
    """
    if not HAS_DOTENV:
        raise ImportError("python-dotenv is required for load_dotjgtset_exported_env function")
    
    dotenv_path = get_dotenv_jgtset_export_path()
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        return True
    else:
        return False


# YAML Environment Functions

def load_jgtyaml_env(config_file: str = "_config.yaml", jgt_key: str = "jgt") -> bool:
    """
    Load JGT environment variables from YAML configuration file.
    
    Args:
        config_file: Path to YAML config file
        jgt_key: Key in YAML file containing JGT environment variables
        
    Returns:
        True if file exists and was loaded, False otherwise
    """
    if not HAS_YAML:
        return False
        
    try:
        with open(config_file) as f:
            config = yaml.load(f)
            jgt_env = config[jgt_key]
            for key in jgt_env:
                os.environ[key] = str(jgt_env[key])
            return True
    except Exception as e:
        return False


# Comprehensive Environment Loading

def load_env() -> bool:
    """
    Load environment variables from all available JGT sources.
    
    Attempts to load from:
    - .jgt/env.sh
    - .env.jgtset (exported settings)
    - .env.fxtrade (FX trading settings)
    - _config.yaml (YAML configuration)
    
    Returns:
        True if any environment file was loaded, False if none found
    """
    _load_dotjgt_env_sh = load_dotjgt_env_sh()
    _load_dotjgtset_exported_env = load_dotjgtset_exported_env()
    _load_dotfxtrade_env = load_dotfxtrade_env()
    _load_jgtyaml_env = load_jgtyaml_env()
    
    if _load_dotjgt_env_sh or _load_dotjgtset_exported_env or _load_dotfxtrade_env or _load_jgtyaml_env:
        return True
    return False


# OpenAI API Key Helper

def get_openai_key() -> Optional[str]:
    """
    Read OpenAI API key from environment or .env files.
    
    Searches for OPENAI_API_KEY in:
    1. Current environment variables
    2. .env file in parent directory
    3. .env file in grandparent directory  
    4. .env file in home directory
    
    Returns:
        OpenAI API key or None if not found
    """
    # Check if already in environment
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        return api_key
    
    if not HAS_DOTENV:
        return None
    
    # Define the possible locations for the .env file
    dotenv_paths = [
        os.path.join(os.path.dirname(__file__), '..', '.env'),  # Parent directory
        os.path.join(os.path.dirname(__file__), '..', '..', '.env'),  # Grandparent directory
        os.path.join(os.path.expanduser("~"), ".env"),  # Home directory
    ]

    # Try to load the .env file from the possible locations
    for dotenv_path in dotenv_paths:
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                return api_key

    return None


# Argument Loading from JGT Environment

def load_arg_from_jgt_env(argname: str, alias: Optional[str] = None) -> Optional[str]:
    """
    Load argument value from JGT environment variables.
    
    Args:
        argname: Primary argument name to look up
        alias: Alternative argument name to try
        
    Returns:
        Environment variable value or None if not found
    """
    # Try primary name first
    value = os.getenv(argname.upper())
    if value:
        return value
    
    # Try with JGT_ prefix
    value = os.getenv(f"JGT_{argname.upper()}")
    if value:
        return value
    
    # Try alias if provided
    if alias:
        value = os.getenv(alias.upper())
        if value:
            return value
        
        value = os.getenv(f"JGT_{alias.upper()}")
        if value:
            return value
    
    return None


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