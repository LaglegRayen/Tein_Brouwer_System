"""
Validation utilities for the Local Ranking Grid Service
"""

from typing import Union


def validate_coordinates(lat: float, lng: float) -> None:
    """
    Validate latitude and longitude coordinates
    
    Args:
        lat: Latitude
        lng: Longitude
        
    Raises:
        ValueError: If coordinates are invalid
    """
    if not isinstance(lat, (int, float)):
        raise ValueError(f"Latitude must be a number, got {type(lat)}")
    
    if not isinstance(lng, (int, float)):
        raise ValueError(f"Longitude must be a number, got {type(lng)}")
    
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
    
    if not (-180 <= lng <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {lng}")


def validate_grid_parameters(grid_size: int, radius_km: float) -> None:
    """
    Validate grid size and radius parameters
    
    Args:
        grid_size: Size of the grid
        radius_km: Radius in kilometers
        
    Raises:
        ValueError: If parameters are invalid
    """
    if not isinstance(grid_size, int):
        raise ValueError(f"Grid size must be an integer, got {type(grid_size)}")
    
    if not (1 <= grid_size <= 10):
        raise ValueError(f"Grid size must be between 1 and 10, got {grid_size}")
    
    if not isinstance(radius_km, (int, float)):
        raise ValueError(f"Radius must be a number, got {type(radius_km)}")
    
    if not (0.1 <= radius_km <= 50):
        raise ValueError(f"Radius must be between 0.1 and 50 km, got {radius_km}")


def validate_business_name(business_name: str) -> None:
    """
    Validate business name
    
    Args:
        business_name: Business name to validate
        
    Raises:
        ValueError: If business name is invalid
    """
    if not isinstance(business_name, str):
        raise ValueError(f"Business name must be a string, got {type(business_name)}")
    
    if not business_name.strip():
        raise ValueError("Business name cannot be empty")
    
    if len(business_name.strip()) < 2:
        raise ValueError("Business name must be at least 2 characters long")
    
    if len(business_name.strip()) > 200:
        raise ValueError("Business name cannot exceed 200 characters")


def validate_language_code(language_code: str) -> None:
    """
    Validate language code
    
    Args:
        language_code: Language code to validate
        
    Raises:
        ValueError: If language code is invalid
    """
    if not isinstance(language_code, str):
        raise ValueError(f"Language code must be a string, got {type(language_code)}")
    
    # Common language codes for DataForSEO
    valid_codes = {
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko',
        'ar', 'hi', 'th', 'vi', 'id', 'ms', 'tr', 'pl', 'nl', 'sv',
        'da', 'no', 'fi', 'cs', 'sk', 'hu', 'ro', 'bg', 'hr', 'sl',
        'et', 'lv', 'lt', 'el', 'he', 'fa', 'ur', 'bn', 'ta', 'te'
    }
    
    if language_code not in valid_codes:
        raise ValueError(f"Invalid language code: {language_code}")


def validate_device_type(device: str) -> None:
    """
    Validate device type
    
    Args:
        device: Device type to validate
        
    Raises:
        ValueError: If device type is invalid
    """
    if not isinstance(device, str):
        raise ValueError(f"Device type must be a string, got {type(device)}")
    
    valid_devices = {'desktop', 'mobile', 'tablet'}
    
    if device.lower() not in valid_devices:
        raise ValueError(f"Invalid device type: {device}. Must be one of {valid_devices}")


def validate_zoom_level(zoom: int) -> None:
    """
    Validate map zoom level
    
    Args:
        zoom: Zoom level to validate
        
    Raises:
        ValueError: If zoom level is invalid
    """
    if not isinstance(zoom, int):
        raise ValueError(f"Zoom level must be an integer, got {type(zoom)}")
    
    if not (1 <= zoom <= 20):
        raise ValueError(f"Zoom level must be between 1 and 20, got {zoom}")


def validate_polling_parameters(max_wait_time: int, poll_interval: int) -> None:
    """
    Validate polling parameters
    
    Args:
        max_wait_time: Maximum wait time in seconds
        poll_interval: Polling interval in seconds
        
    Raises:
        ValueError: If parameters are invalid
    """
    if not isinstance(max_wait_time, int):
        raise ValueError(f"Max wait time must be an integer, got {type(max_wait_time)}")
    
    if not isinstance(poll_interval, int):
        raise ValueError(f"Poll interval must be an integer, got {type(poll_interval)}")
    
    if max_wait_time < 60:
        raise ValueError("Max wait time must be at least 60 seconds")
    
    if max_wait_time > 3600:
        raise ValueError("Max wait time cannot exceed 1 hour (3600 seconds)")
    
    if poll_interval < 30:
        raise ValueError("Poll interval must be at least 30 seconds")
    
    if poll_interval > 600:
        raise ValueError("Poll interval cannot exceed 10 minutes (600 seconds)")
    
    if poll_interval >= max_wait_time:
        raise ValueError("Poll interval must be less than max wait time")


def sanitize_business_name(business_name: str) -> str:
    """
    Sanitize business name for API use
    
    Args:
        business_name: Raw business name
        
    Returns:
        Sanitized business name
    """
    if not isinstance(business_name, str):
        return str(business_name)
    
    # Remove extra whitespace and normalize
    sanitized = ' '.join(business_name.strip().split())
    
    # Remove potentially problematic characters
    sanitized = sanitized.replace('"', '').replace("'", "").replace('\n', ' ').replace('\r', ' ')
    
    return sanitized[:200]  # Truncate to max length
