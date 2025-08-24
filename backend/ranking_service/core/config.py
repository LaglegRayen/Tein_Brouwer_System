"""
Configuration file for DataForSEO credentials and settings
Enhanced for production use with Django integration
"""

import os
import base64
from typing import Optional
from django.conf import settings

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class DataForSEOConfig:
    """Configuration class for DataForSEO API credentials"""
    
    # Method 1: Set your credentials directly here (for testing)
    # IMPORTANT: Don't commit real credentials to version control!
    USERNAME = "your_dataforseo_username_here"
    PASSWORD = "your_dataforseo_password_here"
    
    # Method 4: Base64 encoded credentials (format: username:password)
    # Set this to your base64 encoded "username:password" string
    BASE64_CREDENTIALS = "cmF5ZW4ubGFnbGVnQGFpbWF0aW9uYXRpb24uY29tOjdjODVhMjI1ODYyYWU5MWU="
    
    @classmethod
    def get_credentials(cls) -> tuple[Optional[str], Optional[str]]:
        """
        Get credentials in order of priority:
        1. Django settings (highest priority)
        2. Environment variables 
        3. Base64 encoded credentials
        4. Configuration file values
        5. None if not found
        
        Returns:
            Tuple of (username, password)
        """
        # Try Django settings first (production)
        try:
            django_username = getattr(settings, 'DATAFORSEO_USERNAME', None)
            django_password = getattr(settings, 'DATAFORSEO_PASSWORD', None)
            
            if django_username and django_password:
                logger.info("Using credentials from Django settings")
                return django_username, django_password
        except Exception:
            # Django not available or settings not configured
            pass
        
        # Try environment variables
        env_username = os.getenv('DATAFORSEO_USERNAME')
        env_password = os.getenv('DATAFORSEO_PASSWORD')
        
        if env_username and env_password:
            logger.info("Using credentials from environment variables")
            return env_username, env_password
        
        # Try base64 encoded credentials
        if cls.BASE64_CREDENTIALS and cls.BASE64_CREDENTIALS != "your_base64_credentials_here":
            try:
                decoded = base64.b64decode(cls.BASE64_CREDENTIALS).decode('utf-8')
                if ':' in decoded:
                    username, password = decoded.split(':', 1)
                    logger.info("Using credentials from base64 encoded string")
                    return username, password
                else:
                    logger.warning("Base64 credentials invalid format (should be username:password)")
            except Exception as e:
                logger.error(f"Error decoding base64 credentials: {e}")
        
        # Try config file values
        if cls.USERNAME != "your_dataforseo_username_here" and cls.PASSWORD != "your_dataforseo_password_here":
            logger.info("Using credentials from config file")
            return cls.USERNAME, cls.PASSWORD
        
        logger.warning("No credentials found!")
        return None, None
    
    @classmethod
    def validate_credentials(cls, username: Optional[str], password: Optional[str]) -> bool:
        """
        Validate that credentials are properly set
        
        Args:
            username: DataForSEO username
            password: DataForSEO password
            
        Returns:
            True if credentials appear valid
        """
        if not username or not password:
            logger.error("Missing username or password")
            return False
        
        if username == "your_dataforseo_username_here":
            logger.error("Username not set (still placeholder)")
            return False
        
        if password == "your_dataforseo_password_here":
            logger.error("Password not set (still placeholder)")
            return False
        
        if len(username) < 3:
            logger.error("Username too short")
            return False
        
        if len(password) < 8:
            logger.error("Password too short")
            return False
        
        logger.info("Credentials appear valid")
        return True
    
    @classmethod
    def test_api_connection(cls) -> bool:
        """
        Test API connection with current credentials
        
        Returns:
            True if connection successful
        """
        username, password = cls.get_credentials()
        
        if not cls.validate_credentials(username, password):
            return False
        
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            # Create session with retry strategy
            session = requests.Session()
            retries = Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504]
            )
            session.mount('https://', HTTPAdapter(max_retries=retries))
            
            # Test endpoints
            endpoints = [
                "https://api.dataforseo.com/v3/serp/google/organic/task_post",  # For creating tasks
                "https://api.dataforseo.com/v3/serp/google/organic/task_get/regular"  # For getting results
            ]
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Testing endpoint: {endpoint}")
                    # Different test data based on endpoint
                    if 'task_post' in endpoint:
                        test_data = {
                            "keyword": "test business",
                            "location_code": 2840,  # USA
                            "language_code": "en",
                            "device": "desktop"
                        }
                        method = 'post'
                    else:  # task_get
                        test_data = None  # GET request doesn't need data
                        method = 'get'
                    
                    response = session.request(
                        method=method,
                        url=endpoint,
                        auth=(username, password),
                        json=[test_data] if test_data else None,  # DataForSEO expects an array for POST
                        timeout=30
                    )
                    
                    # Log response details
                    logger.info(f"Status code: {response.status_code}")
                    
                    try:
                        response_data = response.json()
                        logger.info(f"Response data: {response_data}")
                        
                        if response.status_code == 200:
                            logger.info("Endpoint test successful")
                            return True  # Successfully connected to at least one endpoint
                        elif response.status_code == 401:
                            logger.error("Authentication failed - invalid credentials")
                            return False
                        else:
                            logger.error(f"Unexpected status code: {response.status_code}")
                            logger.error(f"Response text: {response.text}")
                    except ValueError as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        logger.error(f"Raw response: {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"Request failed for {endpoint}: {e}")
                    continue
            
            # If we get here, at least one endpoint worked
            logger.info("API connection test successful")
            return True
                
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False


# Convenience functions
def get_dataforseo_credentials() -> tuple[Optional[str], Optional[str]]:
    """Get DataForSEO credentials using the configuration class"""
    return DataForSEOConfig.get_credentials()


def set_base64_credentials(base64_string: str) -> tuple[Optional[str], Optional[str]]:
    """
    Set base64 credentials and return decoded username/password
    
    Args:
        base64_string: Base64 encoded "username:password" string
        
    Returns:
        Tuple of (username, password) or (None, None) if invalid
    """
    try:
        decoded = base64.b64decode(base64_string).decode('utf-8')
        if ':' in decoded:
            username, password = decoded.split(':', 1)
            DataForSEOConfig.BASE64_CREDENTIALS = base64_string
            logger.info(f"Base64 credentials set for user: {username}")
            return username, password
        else:
            logger.error("Invalid base64 format (should encode 'username:password')")
            return None, None
    except Exception as e:
        logger.error(f"Error decoding base64: {e}")
        return None, None


# Instructions for setting up credentials
SETUP_INSTRUCTIONS = """
=== DataForSEO Credentials Setup ===

Choose ONE of these methods:

Method 1: Django Settings (RECOMMENDED for production)
--------------------------------------------------------
Add to your Django settings.py:
DATAFORSEO_USERNAME = 'your_actual_username'
DATAFORSEO_PASSWORD = 'your_actual_password'

Method 2: Environment Variables (RECOMMENDED for development)
-------------------------------------------------------------
Set these environment variables:
- DATAFORSEO_USERNAME=your_actual_username
- DATAFORSEO_PASSWORD=your_actual_password

Windows:
set DATAFORSEO_USERNAME=your_actual_username
set DATAFORSEO_PASSWORD=your_actual_password

Linux/Mac:
export DATAFORSEO_USERNAME=your_actual_username
export DATAFORSEO_PASSWORD=your_actual_password

Method 3: Base64 Encoded Credentials (SIMPLE for testing)
--------------------------------------------------------
Edit config.py and set:
BASE64_CREDENTIALS = "your_base64_encoded_username:password"

To create base64 string:
echo -n "username:password" | base64

Method 4: Edit config.py (for testing only)
------------------------------------------
Edit this file and replace:
USERNAME = "your_actual_username"
PASSWORD = "your_actual_password"

WARNING: Don't commit real credentials to version control!

Method 5: Pass directly to classes
----------------------------------
GridRankChecker(username="your_user", password="your_pass")

You can get DataForSEO credentials at: https://dataforseo.com/
"""
