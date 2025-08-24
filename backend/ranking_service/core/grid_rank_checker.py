"""
Grid Rank Checker - Main orchestrator for DataForSEO batch task management
Enhanced with comprehensive logging, validation, and Django integration
"""

from typing import Dict, Any, Optional
from datetime import datetime

from ..utils.logging_config import get_logger
from ..utils.validators import (
    validate_coordinates, validate_grid_parameters, 
    validate_business_name, sanitize_business_name
)
from .task_batcher import TaskBatcher
from .results_fetcher import ResultsFetcher
from .coordinate_calculator import CoordinateCalculator
from .config import DataForSEOConfig

logger = get_logger(__name__)


class GridRankChecker:
    """
    Main class that orchestrates grid-based ranking checks
    Enhanced with comprehensive error handling and logging
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize with DataForSEO credentials
        
        Args:
            username: DataForSEO username (will try config/ENV if not provided)
            password: DataForSEO password (will try config/ENV if not provided)
            
        Raises:
            ValueError: If credentials are invalid
        """
        logger.info("Initializing GridRankChecker...")
        
        # Use provided credentials or get from config
        if username and password:
            logger.debug("Using provided credentials")
            self.username = username
            self.password = password
        else:
            logger.debug("Getting credentials from config...")
            self.username, self.password = DataForSEOConfig.get_credentials()
        
        # Validate credentials
        if not DataForSEOConfig.validate_credentials(self.username, self.password):
            logger.error("Invalid DataForSEO credentials")
            raise ValueError(
                "Invalid DataForSEO credentials. Please check your configuration."
            )
        
        logger.info(f"Initialized with username: {self.username}")
        
        # Initialize components
        self.task_batcher = TaskBatcher(self.username, self.password)
        self.results_fetcher = ResultsFetcher(self.username, self.password)
        
        logger.info("GridRankChecker initialization complete")
    
    def create_tasks_only(self, business_name: str, business_lat: float,
                         business_lng: float, **kwargs) -> tuple[list[str], list[str]]:
        """
        Create tasks without waiting for results
        
        Args:
            business_name: Business name to search for
            business_lat: Business latitude
            business_lng: Business longitude
            **kwargs: Additional parameters (grid_size, radius_km, language_code, device)
            
        Returns:
            Tuple of (task_ids, coordinate_strings)
            
        Raises:
            ValueError: If input parameters are invalid
        """
        logger.info(f"Creating grid rank check tasks for: {business_name}")
        
        # Validate and sanitize inputs
        validate_business_name(business_name)
        validate_coordinates(business_lat, business_lng)
        
        business_name = sanitize_business_name(business_name)
        
        logger.info(f"Business: {business_name}")
        logger.info(f"Center coordinates: {business_lat}, {business_lng}")
        
        # Get grid parameters
        grid_size = kwargs.get('grid_size', 3)
        radius_km = kwargs.get('radius_km', 5.0)
        
        validate_grid_parameters(grid_size, radius_km)
        
        # Get coordinates for reference
        coordinates = CoordinateCalculator.generate_task_coordinates(
            business_lat, business_lng, grid_size, radius_km
        )
        
        logger.info(f"Generated {len(coordinates)} grid points in {radius_km}km radius")
        
        try:
            # Create and submit tasks
            task_ids = self.task_batcher.create_and_submit_tasks(
                business_name, business_lat, business_lng, **kwargs
            )
            
            logger.info(f"Successfully created {len(task_ids)} tasks")
            return task_ids, coordinates
            
        except Exception as e:
            logger.error(f"Failed to create tasks: {e}")
            raise
    
    def get_results_only(self, task_ids: list[str], **kwargs) -> Dict[str, Any]:
        """
        Get results for existing task IDs
        
        Args:
            task_ids: List of task IDs to fetch results for
            **kwargs: Additional parameters for polling (max_wait_time, poll_interval)
            
        Returns:
            Results dictionary with completed, failed, and pending tasks
        """
        if not task_ids:
            logger.warning("No task IDs provided")
            return {
                "completed": {}, 
                "failed": {}, 
                "pending": [], 
                "summary": {
                    "total_tasks": 0,
                    "completed_count": 0,
                    "failed_count": 0,
                    "pending_count": 0
                }
            }
        
        logger.info(f"Starting to fetch results for {len(task_ids)} tasks...")
        
        # Set default polling parameters
        polling_params = {
            'max_wait_time': kwargs.get('max_wait_time', 1800),  # 30 minutes
            'poll_interval': kwargs.get('poll_interval', 120)    # 2 minutes
        }
        
        try:
            # Fetch results
            results = self.results_fetcher.get_all_results(task_ids, **polling_params)
            
            logger.info("Results fetching completed")
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch results: {e}")
            raise
    
    def run_grid_check(self, business_name: str, business_lat: float,
                      business_lng: float, **kwargs) -> Dict[str, Any]:
        """
        Complete workflow: create tasks and wait for results
        
        Args:
            business_name: Business name to search for
            business_lat: Business latitude
            business_lng: Business longitude
            **kwargs: Additional parameters for task creation and polling
            
        Returns:
            Complete results including task creation info and final results
        """
        start_time = datetime.now()
        logger.info("Starting complete grid rank check workflow...")
        
        try:
            # Create tasks
            task_ids, coordinates = self.create_tasks_only(
                business_name, business_lat, business_lng, **kwargs
            )
            
            if not task_ids:
                logger.error("Failed to create tasks")
                return {
                    "error": "Failed to create tasks",
                    "task_ids": [],
                    "coordinates": coordinates,
                    "results": {
                        "completed": {}, 
                        "failed": {}, 
                        "pending": [], 
                        "summary": {}
                    },
                    "metadata": {
                        "start_time": start_time.isoformat(),
                        "end_time": datetime.now().isoformat(),
                        "success": False
                    }
                }
            
            # Get results
            results = self.get_results_only(task_ids, **kwargs)
            
            # Compile final response
            end_time = datetime.now()
            final_results = {
                "business_name": business_name,
                "center_coordinates": {"lat": business_lat, "lng": business_lng},
                "grid_parameters": {
                    "size": kwargs.get('grid_size', 3),
                    "radius_km": kwargs.get('radius_km', 5.0)
                },
                "grid_coordinates": coordinates,
                "task_ids": task_ids,
                "results": results,
                "metadata": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "total_duration_seconds": (end_time - start_time).total_seconds(),
                    "success": True
                }
            }
            
            logger.info("Grid rank check workflow completed successfully")
            return final_results
            
        except Exception as e:
            logger.error(f"Grid rank check workflow failed: {e}")
            end_time = datetime.now()
            return {
                "error": str(e),
                "business_name": business_name,
                "center_coordinates": {"lat": business_lat, "lng": business_lng},
                "metadata": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "total_duration_seconds": (end_time - start_time).total_seconds(),
                    "success": False
                }
            }
    
    def quick_check(self, business_name: str, business_lat: float,
                   business_lng: float) -> Dict[str, Any]:
        """
        Quick check with default settings (3x3 grid, 5km radius)
        
        Args:
            business_name: Business name to search for
            business_lat: Business latitude
            business_lng: Business longitude
            
        Returns:
            Complete results
        """
        logger.info(f"Running quick check for {business_name}")
        
        return self.run_grid_check(
            business_name=business_name,
            business_lat=business_lat,
            business_lng=business_lng,
            grid_size=3,
            radius_km=5.0
        )
    
    def get_status(self, task_ids: list[str]) -> Dict[str, Any]:
        """
        Get quick status of tasks without polling
        
        Args:
            task_ids: List of task IDs
            
        Returns:
            Current status of tasks
        """
        if not task_ids:
            return {"status": "no_tasks", "message": "No task IDs provided"}
        
        logger.info(f"Getting status for {len(task_ids)} tasks")
        
        try:
            status = self.results_fetcher.get_quick_status(task_ids)
            return {
                "status": "success",
                "task_count": len(task_ids),
                "task_status": status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Convenience functions for quick usage
def create_grid_rank_checker(username: Optional[str] = None, 
                           password: Optional[str] = None) -> GridRankChecker:
    """
    Create a GridRankChecker instance
    
    Args:
        username: DataForSEO username
        password: DataForSEO password
        
    Returns:
        GridRankChecker instance
    """
    return GridRankChecker(username, password)


def create_grid_rank_checker_from_base64(base64_credentials: str) -> GridRankChecker:
    """
    Create a GridRankChecker instance from base64 encoded credentials
    
    Args:
        base64_credentials: Base64 encoded "username:password" string
        
    Returns:
        GridRankChecker instance
    """
    from .config import set_base64_credentials
    
    username, password = set_base64_credentials(base64_credentials)
    if username and password:
        return GridRankChecker(username, password)
    else:
        raise ValueError("Invalid base64 credentials provided")
