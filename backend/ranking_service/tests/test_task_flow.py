"""Test the complete task flow: create task and poll for results"""
import os
import sys
import time
import django
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saas_project.settings')
django.setup()

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ranking_service.core.config import DataForSEOConfig
from ranking_service.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_task_flow():
    """Test creating a task and polling for results"""
    username, password = DataForSEOConfig.get_credentials()
    
    # Create session with retry strategy
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5)
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    # Step 1: Create task
    create_endpoint = "https://api.dataforseo.com/v3/serp/google/organic/task_post"
    test_data = {
        "keyword": "test business",
        "location_code": 2840,  # USA
        "language_code": "en",
        "device": "desktop"
    }
    
    logger.info("Creating task...")
    try:
        response = session.post(
            create_endpoint,
            auth=(username, password),
            json=[test_data],
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to create task. Status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return
            
        data = response.json()
        logger.info(f"Task creation response: {data}")
        
        # Get task ID from response
        if data.get('tasks'):
            task_id = data['tasks'][0].get('id')
            if not task_id:
                logger.error("No task ID in response")
                return
            logger.info(f"Got task ID: {task_id}")
        else:
            logger.error("No tasks in response")
            return
            
        # Step 2: Poll for results
        results_endpoint = "https://api.dataforseo.com/v3/serp/google/organic/task_get/regular"
        max_attempts = 5  # Try 5 times
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            logger.info(f"\nChecking results (attempt {attempt}/{max_attempts})...")
            
            try:
                response = session.get(
                    f"{results_endpoint}/{task_id}",
                    auth=(username, password),
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get results. Status: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    break
                    
                data = response.json()
                logger.info(f"Results response: {data}")
                
                # Check if results are ready
                if data.get('tasks') and data['tasks'][0].get('result'):
                    logger.info("✅ Results are ready!")
                    return
                else:
                    logger.info("Results not ready yet, waiting 2 minutes...")
                    time.sleep(120)  # Wait 2 minutes before next check
                    
            except Exception as e:
                logger.error(f"Error checking results: {e}")
                break
                
        logger.warning("Max attempts reached, results may not be ready yet")
        
    except Exception as e:
        logger.error(f"Error in task flow: {e}")

if __name__ == '__main__':
    test_task_flow()
