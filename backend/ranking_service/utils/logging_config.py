"""
Logging configuration for the Local Ranking Grid Service
"""

import logging
import os
from pathlib import Path
from datetime import datetime


# Default log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Log levels mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def setup_logger(name: str = 'ranking_service', 
                level: str = 'INFO',
                log_to_file: bool = True,
                log_dir: str = None) -> logging.Logger:
    """
    Set up a logger with console and optional file output
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_dir: Directory for log files (optional)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Set level
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        if log_dir is None:
            # Create logs directory in the ranking service directory
            current_dir = Path(__file__).parent.parent
            log_dir = current_dir / 'logs'
        else:
            log_dir = Path(log_dir)
        
        # Create logs directory if it doesn't exist
        log_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    # Get environment variables for configuration
    log_level = os.getenv('RANKING_SERVICE_LOG_LEVEL', 'INFO')
    log_to_file = os.getenv('RANKING_SERVICE_LOG_TO_FILE', 'true').lower() == 'true'
    
    return setup_logger(
        name=name.replace('.', '_'),  # Replace dots for cleaner file names
        level=log_level,
        log_to_file=log_to_file
    )


# Module-level setup
def configure_django_logging():
    """
    Configure logging for Django integration
    """
    try:
        from django.conf import settings
        
        # Add custom logging configuration to Django settings
        if hasattr(settings, 'LOGGING'):
            ranking_service_config = {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            }
            
            if 'loggers' not in settings.LOGGING:
                settings.LOGGING['loggers'] = {}
            
            settings.LOGGING['loggers']['ranking_service'] = ranking_service_config
    except ImportError:
        # Django not available
        pass


# Configure logging based on environment
if os.getenv('DJANGO_SETTINGS_MODULE'):
    try:
        configure_django_logging()
    except Exception as e:
        print(f"Warning: Failed to configure Django logging: {e}")
        # Fall back to basic configuration
        logging.basicConfig(
            level=logging.INFO,
            format=LOG_FORMAT
        )
