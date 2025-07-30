#!/usr/bin/env python3

"""
jgtcore.timeframe - Core timeframe scheduling library

This module provides the core timeframe logic extracted from jgtutils.timeframe_scheduler
without CLI dependencies, making it suitable for use in other libraries and applications.

Main Functions:
- get_times_by_timeframe_str(): Get timeframe trigger times
- get_current_time(): Get current time in appropriate format
- is_timeframe_reached(): Check if current time matches timeframe
- wait_for_timeframe(): Wait until timeframe is reached (for library use)
- TimeframeChecker: Class-based interface for timeframe monitoring
"""

import datetime
import time
from typing import List, Optional, Union, Callable


def get_current_time(timeframe: str) -> str:
    """
    Get current time formatted appropriately for the timeframe.
    
    Args:
        timeframe: Timeframe string (m1, m5, m15, H1, H4, D1, etc.)
        
    Returns:
        Current time as formatted string
    """
    if timeframe == "m1":
        return datetime.datetime.now().strftime("%H:%M:%S")
    else:
        return datetime.datetime.now().strftime("%H:%M")


def get_times_by_timeframe_str(timeframe: str) -> List[str]:
    """
    Get list of time strings when the timeframe should trigger.
    
    Args:
        timeframe: Timeframe string (m1, m5, m15, H1, H4, D1, W1, M1)
        
    Returns:
        List of time strings when timeframe should trigger
    """
    if timeframe in ["D1", "W1", "M1"]:
        return get_timeframe_daily_ending_time()
    elif timeframe == "H8":
        return get_timeframes_times_by_minutes(8 * 60)
    elif timeframe == "H4":
        return get_timeframes_times_by_minutes(4 * 60)
    elif timeframe == "H3":
        return get_timeframes_times_by_minutes(3 * 60)
    elif timeframe == "H2":
        return get_timeframes_times_by_minutes(2 * 60)
    elif timeframe == "H1":
        return get_timeframes_times_by_minutes(60)
    elif timeframe == "m30":
        return get_timeframes_times_by_minutes(30)
    elif timeframe == "m15":
        return get_timeframes_times_by_minutes(15)
    elif timeframe == "m5":
        return get_timeframes_times_by_minutes(5)
    elif timeframe == "m1":
        return get_timeframes_times_by_minutes(1)
    else:
        raise ValueError(f"Unsupported timeframe: {timeframe}")


def get_timeframes_times_by_minutes(minutes: int) -> List[str]:
    """
    Generate list of times based on minute intervals.
    
    Args:
        minutes: Interval in minutes
        
    Returns:
        List of time strings
    """
    start_range = 1 if minutes >= 60 else 0
    
    if minutes > 1:
        return [f"{str(h).zfill(2)}:{str(m).zfill(2)}" 
                for h in range(start_range, 24) 
                for m in range(0, 60, minutes)]
    elif minutes == 1:
        # For m1, include both :00 and :01 seconds to ensure we catch the timeframe
        times = []
        for h in range(start_range, 24):
            for m in range(0, 60):
                times.append(f"{str(h).zfill(2)}:{str(m).zfill(2)}:00")
                times.append(f"{str(h).zfill(2)}:{str(m).zfill(2)}:01")
        return times
    else:
        raise ValueError(f"Invalid minutes value: {minutes}")


def get_timeframe_daily_ending_time() -> List[str]:
    """
    Get daily timeframe ending time (considering DST).
    
    Returns:
        List containing the daily ending time
    """
    now = datetime.datetime.now()
    year = now.year
    
    # DST calculation: second Sunday in March to first Sunday in November
    dst_start = datetime.datetime(year, 3, 8) + datetime.timedelta(
        days=(6 - datetime.datetime(year, 3, 8).weekday())
    )
    dst_end = datetime.datetime(year, 11, 1) + datetime.timedelta(
        days=(6 - datetime.datetime(year, 11, 1).weekday())
    )
    
    if dst_start <= now < dst_end:
        return ["22:00:00"]
    else:
        return ["21:00:00"]


def is_timeframe_reached(timeframe: str, current_time: Optional[str] = None) -> bool:
    """
    Check if the current time matches the timeframe trigger times.
    
    Args:
        timeframe: Timeframe string
        current_time: Optional current time string (defaults to now)
        
    Returns:
        True if timeframe should trigger now
    """
    if current_time is None:
        current_time = get_current_time(timeframe)
    
    trigger_times = get_times_by_timeframe_str(timeframe)
    return current_time in trigger_times


def wait_for_timeframe(
    timeframe: str, 
    callback: Optional[Callable[[str], None]] = None,
    max_wait_seconds: Optional[int] = None,
    check_interval: int = 1
) -> bool:
    """
    Wait until the specified timeframe is reached.
    
    Args:
        timeframe: Timeframe to wait for
        callback: Optional callback function to call when timeframe is reached
        max_wait_seconds: Maximum seconds to wait (None = wait indefinitely)
        check_interval: How often to check (seconds)
        
    Returns:
        True if timeframe was reached, False if max_wait_seconds exceeded
    """
    start_time = time.time()
    sleep_duration = 60 if timeframe != "m1" else 2
    
    while True:
        current_time = get_current_time(timeframe)
        
        if is_timeframe_reached(timeframe, current_time):
            if callback:
                callback(timeframe)
            return True
        
        # Check if we've exceeded max wait time
        if max_wait_seconds is not None:
            elapsed = time.time() - start_time
            if elapsed >= max_wait_seconds:
                return False
        
        time.sleep(check_interval)


class TimeframeChecker:
    """
    Class-based interface for timeframe monitoring.
    
    This provides a more object-oriented way to work with timeframes,
    useful for integration into larger applications.
    """
    
    def __init__(self, timeframe: str):
        """
        Initialize timeframe checker.
        
        Args:
            timeframe: Timeframe to monitor
        """
        self.timeframe = timeframe
        self.trigger_times = get_times_by_timeframe_str(timeframe)
        self.last_trigger_time = None
        
    def check_now(self) -> bool:
        """
        Check if timeframe should trigger now.
        
        Returns:
            True if timeframe should trigger
        """
        current_time = get_current_time(self.timeframe)
        is_triggered = current_time in self.trigger_times
        
        if is_triggered and current_time != self.last_trigger_time:
            self.last_trigger_time = current_time
            return True
        return False
    
    def get_next_trigger_time(self) -> Optional[str]:
        """
        Get the next time this timeframe will trigger.
        
        Returns:
            Next trigger time string or None if can't determine
        """
        current_time = get_current_time(self.timeframe)
        
        # Find next trigger time after current time
        for trigger_time in self.trigger_times:
            if trigger_time > current_time:
                return trigger_time
        
        # If no trigger time found today, return first trigger time of next day
        if self.trigger_times:
            return self.trigger_times[0]
        
        return None
    
    def seconds_until_next_trigger(self) -> Optional[int]:
        """
        Calculate seconds until next timeframe trigger.
        
        Returns:
            Seconds until next trigger or None if can't calculate
        """
        current_time = get_current_time(self.timeframe)
        
        # Find next trigger time after current time
        for trigger_time in self.trigger_times:
            if trigger_time > current_time:
                now = datetime.datetime.now()
                
                if self.timeframe == "m1":
                    hour, minute, second = map(int, trigger_time.split(':'))
                    next_dt = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
                else:
                    hour, minute = map(int, trigger_time.split(':'))
                    next_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                if next_dt <= now:
                    next_dt += datetime.timedelta(days=1)
                
                delta = next_dt - now
                return int(delta.total_seconds())
        
        return None


# Convenience functions for quick testing
def simulate_timeframe_reached(timeframe: str) -> bool:
    """
    Simulate timeframe reached for testing purposes.
    Always returns True with a small delay.
    
    Args:
        timeframe: Timeframe being simulated
        
    Returns:
        Always True (for testing)
    """
    print(f"🔄 SIMULATION: {timeframe} timeframe reached")
    time.sleep(1)  # Small delay for realism
    return True


def get_sleep_duration_for_timeframe(timeframe: str) -> int:
    """
    Get appropriate sleep duration for timeframe monitoring.
    
    Args:
        timeframe: Timeframe string
        
    Returns:
        Sleep duration in seconds
    """
    if timeframe == "m1":
        return 2
    elif timeframe in ["m5", "m15"]:
        return 30
    elif timeframe in ["H1", "H4"]:
        return 60
    else:
        return 60 