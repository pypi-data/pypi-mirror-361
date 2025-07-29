"""
Memory utility functions for tracking memory usage.
"""

import psutil
from typing import Optional


def get_memory_usage(process: Optional[psutil.Process] = None) -> int:
    """
    Get current memory usage in bytes.
    
    Args:
        process: Process object to check. If None, uses current process.
        
    Returns:
        Memory usage in bytes.
    """
    if process is None:
        process = psutil.Process()
    
    try:
        return process.memory_info().rss
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0


def get_memory_percentage(process: Optional[psutil.Process] = None) -> float:
    """
    Get current memory usage as percentage of total system memory.
    
    Args:
        process: Process object to check. If None, uses current process.
        
    Returns:
        Memory usage as percentage.
    """
    if process is None:
        process = psutil.Process()
    
    try:
        return process.memory_percent()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0.0


def get_system_memory_info() -> dict:
    """
    Get system memory information.
    
    Returns:
        Dictionary with memory information.
    """
    try:
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': memory.percent
        }
    except Exception:
        return {
            'total': 0,
            'available': 0,
            'used': 0,
            'free': 0,
            'percent': 0.0
        } 