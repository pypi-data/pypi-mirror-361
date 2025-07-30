"""
FX trading utilities for jgtcore

Core FX transaction data handling migrated from jgtutils.
Provides data structures and utilities for managing FX trades and orders
without CLI dependencies.
"""

import datetime
import json
import os
from typing import List, Dict, Any, Optional, Union

# Optional YAML support - graceful fallback to JSON-only if not available
try:
    import ruamel.yaml
    yaml = ruamel.yaml.YAML()
    HAS_YAML = True
except ImportError:
    yaml = None
    HAS_YAML = False

# File prefixes for FX operations
ORDER_FILE_PREFIX = "order_"
TRADE_FILE_PREFIX = "trade_"
TRADES_FILE_PREFIX = "trades"
ORDERS_FILE_PREFIX = "orders"
FXTRANSAC_FILE_PREFIX = "fxtransact"
TRADE_FXMVSTOP_PREFIX = "fxmvstop_"
ORDER_ADD_PREFIX = "fxaddorder_"
ORDER_RM_PREFIX = "fxrmorder_"
TRADE_FXRM_PREFIX = "fxrmtrade_"
FXREPORT_FILE_PREFIX = "fxreport_"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for file operations
    """
    # Basic filename sanitization - remove/replace problematic characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


class FXTrade:
    """
    Represents an FX trade with comprehensive trade data.
    
    Core data structure for individual FX trading transactions.
    """
    
    def __init__(self, trade_id: Optional[str] = None, instrument: Optional[str] = None,
                 amount: Optional[float] = None, buy_sell: Optional[str] = None,
                 open_rate: Optional[float] = None, close_rate: Optional[float] = None,
                 open_time: Optional[str] = None, close_time: Optional[str] = None,
                 pl: Optional[float] = None, **kwargs):
        """
        Initialize FX trade.
        
        Args:
            trade_id: Unique trade identifier
            instrument: Currency pair (e.g., "EUR/USD")
            amount: Trade amount
            buy_sell: Trade direction ("B" or "S")
            open_rate: Opening rate
            close_rate: Closing rate
            open_time: Trade opening timestamp
            close_time: Trade closing timestamp
            pl: Profit/loss
            **kwargs: Additional trade data
        """
        self.trade_id = trade_id
        self.instrument = instrument
        self.amount = amount
        self.buy_sell = buy_sell
        self.open_rate = open_rate
        self.close_rate = close_rate
        self.open_time = open_time
        self.close_time = close_time
        self.pl = pl
        
        # Store additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trade to dictionary."""
        return {
            'trade_id': self.trade_id,
            'instrument': self.instrument,
            'amount': self.amount,
            'buy_sell': self.buy_sell,
            'open_rate': self.open_rate,
            'close_rate': self.close_rate,
            'open_time': self.open_time,
            'close_time': self.close_time,
            'pl': self.pl
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert trade to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_yaml(self) -> str:
        """Convert trade to YAML string."""
        if not HAS_YAML:
            raise ImportError("ruamel.yaml is required for YAML output")
        return yaml.dump(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FXTrade':
        """Create trade from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json_string(cls, json_str: str) -> 'FXTrade':
        """Create trade from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class FXTrades:
    """
    Collection wrapper for multiple FX trades.
    
    Manages a collection of FXTrade objects with serialization capabilities.
    """
    
    def __init__(self, trades: Optional[List[FXTrade]] = None):
        """
        Initialize trades collection.
        
        Args:
            trades: List of FXTrade objects
        """
        self.trades = trades or []
    
    def add_trade(self, trade_data: Union[FXTrade, str, Dict[str, Any]]):
        """
        Add trade to collection.
        
        Args:
            trade_data: FXTrade object, JSON string, or dictionary
        """
        if isinstance(trade_data, FXTrade):
            self.trades.append(trade_data)
        elif isinstance(trade_data, str):
            try:
                trade = FXTrade.from_json_string(trade_data)
                self.trades.append(trade)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON string: {trade_data}")
        elif isinstance(trade_data, dict):
            trade = FXTrade.from_dict(trade_data)
            self.trades.append(trade)
        else:
            raise TypeError("trade_data must be FXTrade, string, or dict")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trades collection to dictionary."""
        return {
            "trades": [trade.to_dict() for trade in self.trades]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert trades collection to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_yaml(self) -> str:
        """Convert trades collection to YAML string."""
        if not HAS_YAML:
            raise ImportError("ruamel.yaml is required for YAML output")
        return yaml.dump(self.to_dict())
    
    def get_filename(self, ext: str = "json", prefix: str = TRADES_FILE_PREFIX) -> str:
        """Generate filename for trades collection."""
        return sanitize_filename(f"{prefix}.{ext}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FXTrades':
        """Create trades collection from dictionary."""
        trades = [FXTrade.from_dict(trade_data) for trade_data in data.get('trades', [])]
        return cls(trades)
    
    @classmethod
    def from_json_string(cls, json_str: str) -> 'FXTrades':
        """Create trades collection from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class FXOrder:
    """
    Represents an FX order with detailed order information.
    
    Core data structure for FX order management.
    """
    
    def __init__(self, order_id: Optional[str] = None, instrument: Optional[str] = None,
                 amount: Optional[float] = None, buy_sell: Optional[str] = None,
                 rate: Optional[float] = None, stop: Optional[float] = None,
                 limit: Optional[float] = None, status: Optional[str] = None,
                 time_in_force: Optional[str] = None, **kwargs):
        """
        Initialize FX order.
        
        Args:
            order_id: Unique order identifier
            instrument: Currency pair
            amount: Order amount
            buy_sell: Order direction ("B" or "S")
            rate: Order rate
            stop: Stop loss rate
            limit: Limit rate
            status: Order status
            time_in_force: Order time in force
            **kwargs: Additional order data
        """
        self.order_id = order_id
        self.instrument = instrument
        self.amount = amount
        self.buy_sell = buy_sell
        self.rate = rate
        self.stop = stop
        self.limit = limit
        self.status = status
        self.time_in_force = time_in_force
        
        # Store additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary."""
        return {
            'order_id': self.order_id,
            'instrument': self.instrument,
            'amount': self.amount,
            'buy_sell': self.buy_sell,
            'rate': self.rate,
            'stop': self.stop,
            'limit': self.limit,
            'status': self.status,
            'time_in_force': self.time_in_force
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert order to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_yaml(self) -> str:
        """Convert order to YAML string."""
        if not HAS_YAML:
            raise ImportError("ruamel.yaml is required for YAML output")
        return yaml.dump(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FXOrder':
        """Create order from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json_string(cls, json_str: str) -> 'FXOrder':
        """Create order from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class FXOrders:
    """
    Collection wrapper for multiple FX orders.
    
    Manages a collection of FXOrder objects with serialization capabilities.
    """
    
    def __init__(self, orders: Optional[List[FXOrder]] = None):
        """
        Initialize orders collection.
        
        Args:
            orders: List of FXOrder objects
        """
        self.orders = orders or []
    
    def add_order(self, order_data: Union[FXOrder, str, Dict[str, Any]]):
        """
        Add order to collection.
        
        Args:
            order_data: FXOrder object, JSON string, or dictionary
        """
        if isinstance(order_data, FXOrder):
            self.orders.append(order_data)
        elif isinstance(order_data, str):
            try:
                order = FXOrder.from_json_string(order_data)
                self.orders.append(order)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON string: {order_data}")
        elif isinstance(order_data, dict):
            order = FXOrder.from_dict(order_data)
            self.orders.append(order)
        else:
            raise TypeError("order_data must be FXOrder, string, or dict")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert orders collection to dictionary."""
        return {
            "orders": [order.to_dict() for order in self.orders]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert orders collection to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_yaml(self) -> str:
        """Convert orders collection to YAML string."""
        if not HAS_YAML:
            raise ImportError("ruamel.yaml is required for YAML output")
        return yaml.dump(self.to_dict())
    
    def get_filename(self, ext: str = "json", prefix: str = ORDERS_FILE_PREFIX) -> str:
        """Generate filename for orders collection."""
        return sanitize_filename(f"{prefix}.{ext}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FXOrders':
        """Create orders collection from dictionary."""
        orders = [FXOrder.from_dict(order_data) for order_data in data.get('orders', [])]
        return cls(orders)
    
    @classmethod
    def from_json_string(cls, json_str: str) -> 'FXOrders':
        """Create orders collection from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class FXTransactWrapper:
    """
    High-level wrapper that combines FX trades and orders.
    
    Unified interface for managing both trades and orders together.
    """
    
    def __init__(self, trades: Optional[FXTrades] = None, orders: Optional[FXOrders] = None):
        """
        Initialize FX transaction wrapper.
        
        Args:
            trades: FXTrades collection
            orders: FXOrders collection
        """
        self.trades = trades or FXTrades()
        self.orders = orders or FXOrders()
    
    def add_trade(self, trade_data: Union[FXTrade, str, Dict[str, Any]]):
        """Add trade to trades collection."""
        self.trades.add_trade(trade_data)
    
    def add_order(self, order_data: Union[FXOrder, str, Dict[str, Any]]):
        """Add order to orders collection."""
        self.orders.add_order(order_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert wrapper to dictionary."""
        return {
            "trades": [trade.to_dict() for trade in self.trades.trades],
            "orders": [order.to_dict() for order in self.orders.orders]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert wrapper to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_yaml(self) -> str:
        """Convert wrapper to YAML string."""
        if not HAS_YAML:
            raise ImportError("ruamel.yaml is required for YAML output")
        return yaml.dump(self.to_dict())
    
    def get_filename(self, ext: str = "json", prefix: str = FXTRANSAC_FILE_PREFIX) -> str:
        """Generate filename for transaction data."""
        return sanitize_filename(f"{prefix}.{ext}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FXTransactWrapper':
        """Create wrapper from dictionary."""
        trades = FXTrades.from_dict({"trades": data.get("trades", [])})
        orders = FXOrders.from_dict({"orders": data.get("orders", [])})
        return cls(trades, orders)
    
    @classmethod
    def from_json_string(cls, json_str: str) -> 'FXTransactWrapper':
        """Create wrapper from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class FXTransactDataHelper:
    """
    Static utility class for FX transaction data operations.
    
    Provides helper methods for loading, saving, and managing FX data files.
    """
    
    @staticmethod
    def save_trades_json(trades: FXTrades, filepath: str, indent: int = 2) -> bool:
        """
        Save trades to JSON file.
        
        Args:
            trades: FXTrades collection
            filepath: Target file path
            indent: JSON indentation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                f.write(trades.to_json(indent))
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_trades_json(filepath: str) -> Optional[FXTrades]:
        """
        Load trades from JSON file.
        
        Args:
            filepath: Source file path
            
        Returns:
            FXTrades collection or None if failed
        """
        try:
            with open(filepath, 'r') as f:
                json_str = f.read()
            return FXTrades.from_json_string(json_str)
        except Exception:
            return None
    
    @staticmethod
    def save_orders_json(orders: FXOrders, filepath: str, indent: int = 2) -> bool:
        """
        Save orders to JSON file.
        
        Args:
            orders: FXOrders collection
            filepath: Target file path
            indent: JSON indentation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                f.write(orders.to_json(indent))
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_orders_json(filepath: str) -> Optional[FXOrders]:
        """
        Load orders from JSON file.
        
        Args:
            filepath: Source file path
            
        Returns:
            FXOrders collection or None if failed
        """
        try:
            with open(filepath, 'r') as f:
                json_str = f.read()
            return FXOrders.from_json_string(json_str)
        except Exception:
            return None
    
    @staticmethod
    def save_wrapper_json(wrapper: FXTransactWrapper, filepath: str, indent: int = 2) -> bool:
        """
        Save transaction wrapper to JSON file.
        
        Args:
            wrapper: FXTransactWrapper instance
            filepath: Target file path
            indent: JSON indentation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                f.write(wrapper.to_json(indent))
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_wrapper_json(filepath: str) -> Optional[FXTransactWrapper]:
        """
        Load transaction wrapper from JSON file.
        
        Args:
            filepath: Source file path
            
        Returns:
            FXTransactWrapper instance or None if failed
        """
        try:
            with open(filepath, 'r') as f:
                json_str = f.read()
            return FXTransactWrapper.from_json_string(json_str)
        except Exception:
            return None


# Legacy aliases for backward compatibility
ftdh = FXTransactDataHelper
ftw = FXTransactWrapper


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