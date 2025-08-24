"""Test DataForSEO credentials"""
import os
import sys
import django
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saas_project.settings')
django.setup()

from ranking_service.core.config import DataForSEOConfig
from ranking_service.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_credentials():
    """Test if DataForSEO credentials are valid and working"""
    logger.info("=== Testing DataForSEO Credentials ===")
    
    # Get credentials
    username, password = DataForSEOConfig.get_credentials()
    logger.info(f"Got credentials - Username: {username}")
    
    # Validate format
    if DataForSEOConfig.validate_credentials(username, password):
        logger.info("✅ Credentials format is valid")
    else:
        logger.error("❌ Invalid credentials format")
        return False
    
    # Test API connection
    logger.info("\nTesting API connection...")
    
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    # Create session with retry strategy
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5)
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    # Test both task creation and results endpoints
    endpoints = [
        "https://api.dataforseo.com/v3/serp/google/organic/task_post",  # For creating tasks
        "https://api.dataforseo.com/v3/serp/google/organic/task_get/regular"  # For getting results
    ]
    
    success = False
    for endpoint in endpoints:
        logger.info(f"\nTesting endpoint: {endpoint}")
        try:
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
                json=[test_data] if test_data else None,
                timeout=30
            )
            
            logger.info(f"Status code: {response.status_code}")
            
            try:
                data = response.json()
                logger.info(f"Response data: {data}")
                
                if response.status_code == 200:
                    logger.info("✅ Endpoint test successful")
                    success = True
                elif response.status_code == 401:
                    logger.error("❌ Authentication failed - invalid credentials")
                else:
                    logger.error(f"❌ Unexpected status code: {response.status_code}")
                    
            except ValueError as e:
                logger.error(f"❌ Failed to parse response as JSON: {e}")
                logger.error(f"Raw response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request failed: {e}")
    
    if success:
        logger.info("\n✅ Successfully connected to DataForSEO API")
        return True
    else:
        logger.error("\n❌ Failed to connect to DataForSEO API")
        return False

if __name__ == '__main__':
    test_credentials()