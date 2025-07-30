"""
FX trading utilities module for jgtcore

This module contains FX trading-related functions migrated from jgtutils:
- FX transaction data structures (FXTrade, FXOrder)
- Collection management (FXTrades, FXOrders)
- High-level transaction wrapper (FXTransactWrapper)
- Data persistence utilities (FXTransactDataHelper)

Provides core FX trading data handling without CLI dependencies.
"""

from .transact import (
    # Core classes
    FXTrade,
    FXTrades, 
    FXOrder,
    FXOrders,
    FXTransactWrapper,
    FXTransactDataHelper,
    
    # Legacy aliases
    ftdh,
    ftw,
    
    # Constants
    ORDER_FILE_PREFIX,
    TRADE_FILE_PREFIX,
    TRADES_FILE_PREFIX,
    ORDERS_FILE_PREFIX,
    FXTRANSAC_FILE_PREFIX,
    TRADE_FXMVSTOP_PREFIX,
    ORDER_ADD_PREFIX,
    ORDER_RM_PREFIX,
    TRADE_FXRM_PREFIX,
    FXREPORT_FILE_PREFIX,
    HAS_YAML,
    
    # Utilities
    sanitize_filename,
)

__all__ = [
    # Core classes
    'FXTrade',
    'FXTrades', 
    'FXOrder',
    'FXOrders',
    'FXTransactWrapper',
    'FXTransactDataHelper',
    
    # Legacy aliases
    'ftdh',
    'ftw',
    
    # Constants
    'ORDER_FILE_PREFIX',
    'TRADE_FILE_PREFIX',
    'TRADES_FILE_PREFIX',
    'ORDERS_FILE_PREFIX',
    'FXTRANSAC_FILE_PREFIX',
    'TRADE_FXMVSTOP_PREFIX',
    'ORDER_ADD_PREFIX',
    'ORDER_RM_PREFIX',
    'TRADE_FXRM_PREFIX',
    'FXREPORT_FILE_PREFIX',
    'HAS_YAML',
    
    # Utilities
    'sanitize_filename',
]