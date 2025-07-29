"""
Formatting utility functions for displaying data in a user-friendly way.
"""

from typing import Union, Optional


def format_bytes(bytes_value: Union[int, float]) -> str:
    """
    Format bytes into human-readable string.
    
    Args:
        bytes_value: Number of bytes.
        
    Returns:
        Formatted string (e.g., "1.5 MB").
    """
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    
    while bytes_value >= 1024 and unit_index < len(units) - 1:
        bytes_value /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(bytes_value)} {units[unit_index]}"
    else:
        return f"{bytes_value:.1f} {units[unit_index]}"


def format_time(seconds: Union[int, float]) -> str:
    """
    Format time in seconds into human-readable string.
    
    Args:
        seconds: Time in seconds.
        
    Returns:
        Formatted string (e.g., "1.5s" or "2m 30s").
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.0f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"


def format_percentage(value: float, total: float) -> str:
    """
    Format a percentage value.
    
    Args:
        value: The value to format.
        total: The total value for percentage calculation.
        
    Returns:
        Formatted percentage string.
    """
    if total == 0:
        return "0.0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"


def format_number(value: Union[int, float]) -> str:
    """
    Format a number with appropriate suffixes.
    
    Args:
        value: The number to format.
        
    Returns:
        Formatted number string.
    """
    if value < 1000:
        return str(int(value))
    elif value < 1000000:
        return f"{value / 1000:.1f}K"
    elif value < 1000000000:
        return f"{value / 1000000:.1f}M"
    else:
        return f"{value / 1000000000:.1f}B"


def format_duration(start_time: float, end_time: float) -> str:
    """
    Format duration between two timestamps.
    
    Args:
        start_time: Start timestamp.
        end_time: End timestamp.
        
    Returns:
        Formatted duration string.
    """
    duration = end_time - start_time
    return format_time(duration)


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: The string to truncate.
        max_length: Maximum length of the string.
        
    Returns:
        Truncated string with ellipsis if needed.
    """
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length-3] + "..."


def format_list(items: list, max_items: int = 5) -> str:
    """
    Format a list of items for display.
    
    Args:
        items: List of items to format.
        max_items: Maximum number of items to show.
        
    Returns:
        Formatted string representation of the list.
    """
    if not items:
        return "[]"
    
    if len(items) <= max_items:
        return str(items)
    else:
        shown_items = items[:max_items]
        remaining = len(items) - max_items
        return f"{shown_items} ... and {remaining} more" 