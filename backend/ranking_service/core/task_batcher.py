import requests
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..utils.logging_config import get_logger
from ..utils.validators import validate_coordinates, validate_grid_parameters
from .coordinate_calculator import CoordinateCalculator

logger = get_logger(__name__)


class TaskBatcher:
    """
    Handles batch creation of DataForSEO tasks for grid-based ranking checks
    """
    
    def __init__(self, username: str, password: str):
        """
        Initialize with DataForSEO credentials
        
        Args:
            username: DataForSEO username
            password: DataForSEO password
        """
        self.username = username
        self.password = password
        self.base_url = "https://api.dataforseo.com/v3/serp/google/maps/task_post"
        self.auth = (username, password)
        logger.info(f"TaskBatcher initialized for user: {username}")
    
    def create_task_payload(self, business_name: str, business_lat: float,
                          business_lng: float, grid_size: int = 3, 
                          radius_km: float = 5.0, language_code: str = "en",
                          device: str = "desktop", zoom: int = 15) -> List[Dict[str, Any]]:
        """
        Create task payloads for all grid coordinates
        
        Args:
            business_name: Business name to search for
            business_lat: Business latitude
            business_lng: Business longitude
            grid_size: Size of the grid (e.g., 3 for 3x3 grid)
            radius_km: Radius in kilometers for the grid
            language_code: Language code for search
            device: Device type (desktop, mobile)
            zoom: Map zoom level
            
        Returns:
            List of task payload dictionaries
        """
        logger.info(f"Creating task payloads for '{business_name}' at {business_lat}, {business_lng}")
        
        # Validate inputs
        validate_coordinates(business_lat, business_lng)
        validate_grid_parameters(grid_size, radius_km)
        
        if not business_name.strip():
            raise ValueError("Business name cannot be empty")
        
        # Generate coordinates
        coordinates = CoordinateCalculator.generate_task_coordinates(
            business_lat, business_lng, grid_size, radius_km, zoom
        )
        
        tasks = []
        for i, coordinate in enumerate(coordinates):
            task = {
                "keyword": business_name.strip(),
                "location_coordinate": coordinate,
                "language_code": language_code,
                "device": device,
                "tag": f"grid_point_{i+1}_{len(coordinates)}"
            }
            tasks.append(task)
        
        logger.info(f"Created {len(tasks)} task payloads")
        return tasks
    
    def submit_tasks(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """
        Submit tasks to DataForSEO API
        
        Args:
            tasks: List of task payload dictionaries
            
        Returns:
            List of task IDs
            
        Raises:
            requests.RequestException: If API request fails
        """
        if not tasks:
            logger.warning("No tasks to submit")
            return []
        
        logger.info(f"Submitting {len(tasks)} tasks to DataForSEO API")
        
        try:
            response = requests.post(
                self.base_url,
                auth=self.auth,
                headers={"Content-Type": "application/json"},
                json=tasks,
                timeout=60
            )
            
            logger.debug(f"API Response Status: {response.status_code}")
            response.raise_for_status()
            
            api_response = response.json()
            
            # Extract task IDs
            task_ids = []
            if "tasks" in api_response:
                for task in api_response["tasks"]:
                    if task.get("status_code") == 20100:  # Task created successfully
                        task_id = task.get("id")
                        if task_id:
                            task_ids.append(task_id)
                            logger.debug(f"Task created with ID: {task_id}")
                    else:
                        logger.warning(f"Task creation failed: {task.get('status_message', 'Unknown error')}")
            
            logger.info(f"Successfully submitted {len(task_ids)} tasks")
            return task_ids
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode API response: {e}")
            raise
    
    def create_and_submit_tasks(self, business_name: str, business_lat: float,
                              business_lng: float, **kwargs) -> List[str]:
        """
        Create and submit tasks in one operation
        
        Args:
            business_name: Business name to search for
            business_lat: Business latitude
            business_lng: Business longitude
            **kwargs: Additional parameters for task creation
            
        Returns:
            List of task IDs
        """
        logger.info(f"Creating and submitting tasks for '{business_name}'")
        
        try:
            # Create task payloads
            tasks = self.create_task_payload(
                business_name, business_lat, business_lng, **kwargs
            )
            
            # Submit tasks
            task_ids = self.submit_tasks(tasks)
            
            logger.info(f"Successfully created and submitted {len(task_ids)} tasks")
            return task_ids
            
        except Exception as e:
            logger.error(f"Failed to create and submit tasks: {e}")
            raise
    
    def get_task_info(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Get information about submitted tasks
        
        Args:
            task_ids: List of task IDs
            
        Returns:
            Task information summary
        """
        if not task_ids:
            return {"total_tasks": 0, "submitted_at": None}
        
        return {
            "total_tasks": len(task_ids),
            "task_ids": task_ids,
            "submitted_at": datetime.now().isoformat(),
            "estimated_completion": "2-30 minutes (DataForSEO processing time)"
        }
