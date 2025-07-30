"""
CLI helper utilities for jgtcore

Helper functions for CLI operations including JSON output formatting
and signal handling migrated from jgtutils.
"""

import json
import sys
import signal
from typing import Optional, Dict, Any, Callable


# Global variables for signal handling
_exit_message = None
_exit_handler = None


def print_jsonl_message(msg: str, extra_dict: Optional[Dict[str, Any]] = None,
                       scope: Optional[str] = None, state: Optional[str] = None,
                       msg_key_name: str = "message", state_key_name: str = "state",
                       scope_key: str = "scope", use_short: bool = False):
    """
    Print a JSON-formatted message to stdout.
    
    Args:
        msg: The main message content
        extra_dict: Additional key-value pairs to include
        scope: Optional scope identifier
        state: Optional state identifier
        msg_key_name: Key name for the message field
        state_key_name: Key name for the state field
        scope_key: Key name for the scope field
        use_short: Whether to use shortened key names
    """
    json_output = build_jsonl_message(
        msg, extra_dict, scope, state, msg_key_name, state_key_name, scope_key, use_short
    )
    print(json_output)


def build_jsonl_message(msg: str, extra_dict: Optional[Dict[str, Any]] = None,
                       scope: Optional[str] = None, state: Optional[str] = None,
                       msg_key_name: str = "message", state_key_name: str = "state",
                       scope_key: str = "scope", use_short: bool = False) -> str:
    """
    Build a JSON-formatted message string.
    
    Args:
        msg: The main message content
        extra_dict: Additional key-value pairs to include
        scope: Optional scope identifier
        state: Optional state identifier
        msg_key_name: Key name for the message field
        state_key_name: Key name for the state field
        scope_key: Key name for the scope field
        use_short: Whether to use shortened key names
        
    Returns:
        JSON-formatted message string
    """
    output = {}
    
    if use_short:
        msg_key_name = "msg"
        state_key_name = "s"
        scope_key = "sc"
    
    output[msg_key_name] = msg
    
    if extra_dict:
        output.update(extra_dict)
    
    if scope:
        output[scope_key] = scope
    
    if state:
        output[state_key_name] = state
    
    return json.dumps(output)


def signal_handler(sig, frame):
    """
    Handle interrupt signals gracefully.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    global _exit_message, _exit_handler
    
    if _exit_message:
        print(_exit_message)
    
    if _exit_handler:
        try:
            msg = _exit_handler()
            if msg:
                print(msg)
        except Exception as e:
            print(f"Error in exit handler: {e}")
    
    sys.exit(0)


def add_exiting_quietly(message: Optional[str] = None,
                       exit_handler: Optional[Callable[[], str]] = None):
    """
    Set up graceful exit handling with optional message and handler.
    
    Args:
        message: Message to display on exit
        exit_handler: Function to call on exit (should return string message)
    """
    global _exit_message, _exit_handler
    
    if exit_handler:
        _exit_handler = exit_handler
    
    if message:
        _exit_message = message
    
    signal.signal(signal.SIGINT, signal_handler)


def print_error_message(msg: str, extra_dict: Optional[Dict[str, Any]] = None,
                       scope: Optional[str] = None):
    """
    Print an error message in JSON format.
    
    Args:
        msg: Error message
        extra_dict: Additional error details
        scope: Optional scope identifier
    """
    print_jsonl_message(msg, extra_dict, scope, state="error")


def print_success_message(msg: str, extra_dict: Optional[Dict[str, Any]] = None,
                         scope: Optional[str] = None):
    """
    Print a success message in JSON format.
    
    Args:
        msg: Success message
        extra_dict: Additional success details
        scope: Optional scope identifier
    """
    print_jsonl_message(msg, extra_dict, scope, state="success")


def print_warning_message(msg: str, extra_dict: Optional[Dict[str, Any]] = None,
                         scope: Optional[str] = None):
    """
    Print a warning message in JSON format.
    
    Args:
        msg: Warning message
        extra_dict: Additional warning details
        scope: Optional scope identifier
    """
    print_jsonl_message(msg, extra_dict, scope, state="warning")


def print_info_message(msg: str, extra_dict: Optional[Dict[str, Any]] = None,
                      scope: Optional[str] = None):
    """
    Print an info message in JSON format.
    
    Args:
        msg: Info message
        extra_dict: Additional info details
        scope: Optional scope identifier
    """
    print_jsonl_message(msg, extra_dict, scope, state="info")


# Legacy alias for backward compatibility
printl = print_jsonl_message


__all__ = [
    'print_jsonl_message',
    'build_jsonl_message',
    'signal_handler',
    'add_exiting_quietly',
    'print_error_message',
    'print_success_message',
    'print_warning_message',
    'print_info_message',
    'printl',  # Legacy alias
]