"""
Logging utility for Ragify
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "ragify",
    level: int = logging.INFO,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger for Ragify
    
    Args:
        name: Logger name
        level: Logging level
        log_format: Custom log format string
        
    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def get_logger(name: str = "ragify") -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name) 