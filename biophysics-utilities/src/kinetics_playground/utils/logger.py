"""
Logging utilities for the kinetics playground.

Provides structured logging with different levels and formats.
"""

import logging
import sys
from typing import Optional
from pathlib import Path


# Color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""
    
    FORMATS = {
        logging.DEBUG: Colors.CYAN + '%(levelname)s' + Colors.RESET + ' - %(message)s',
        logging.INFO: Colors.GREEN + '%(levelname)s' + Colors.RESET + ' - %(message)s',
        logging.WARNING: Colors.YELLOW + '%(levelname)s' + Colors.RESET + ' - %(message)s',
        logging.ERROR: Colors.RED + '%(levelname)s' + Colors.RESET + ' - %(message)s',
        logging.CRITICAL: Colors.BOLD + Colors.RED + '%(levelname)s' + Colors.RESET + ' - %(message)s',
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(
    name: str = 'kinetics_playground',
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_color: bool = True
) -> logging.Logger:
    """
    Get or create a logger with the specified configuration.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging to file
        use_color: Whether to use colored output for console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if use_color and sys.stdout.isatty():
            console_handler.setFormatter(ColoredFormatter())
        else:
            console_handler.setFormatter(
                logging.Formatter('%(levelname)s - %(message)s')
            )
        
        logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # Log everything to file
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(file_handler)
    
    return logger


def set_log_level(level: int):
    """
    Set logging level for all kinetics_playground loggers.
    
    Args:
        level: Logging level (logging.DEBUG, logging.INFO, etc.)
    """
    logger = logging.getLogger('kinetics_playground')
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


# Module-level logger
logger = get_logger()


# Context manager for temporary log level changes
class temporary_log_level:
    """Context manager for temporarily changing log level."""
    
    def __init__(self, level: int):
        self.new_level = level
        self.old_level = None
        self.logger = logging.getLogger('kinetics_playground')
    
    def __enter__(self):
        self.old_level = self.logger.level
        set_log_level(self.new_level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        set_log_level(self.old_level)
        return False
