"""
Main orchestrator for the Local Ranking Grid Service
Provides a simplified interface to the core functionality
"""

from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime

from .core.grid_rank_checker import GridRankChecker
from .core.coordinate_calculator import CoordinateCalculator
from .core.task_batcher import TaskBatcher
from .core.results_fetcher import ResultsFetcher
from .utils.logging_config import get_logger
from .utils.validators import (
    validate_business_name,
    validate_coordinates,
    validate_grid_parameters,
    sanitize_business_name
)

logger = get_logger(__name__)


class RankingService:
    """
    Main service class that provides a simplified interface to the ranking functionality
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """Initialize service with optional credentials"""
        self.grid_checker = GridRankChecker(username, password)
        logger.info("RankingService initialized")
    
    def quick_check(self, business_name: str, lat: float, lng: float) -> Dict[str, Any]:
        """
        Perform a quick ranking check with default parameters (3x3 grid, 5km radius)
        
        Args:
            business_name: Name of the business
            lat: Business latitude
            lng: Business longitude
            
        Returns:
            Complete results dictionary
        """
        logger.info(f"Quick check requested for {business_name} at {lat}, {lng}")
        
        try:
            # Validate inputs
            logger.debug("Validating business name...")
            validate_business_name(business_name)
            
            logger.debug("Validating coordinates...")
            validate_coordinates(lat, lng)
            
            # Sanitize business name
            logger.debug("Sanitizing business name...")
            sanitized_name = sanitize_business_name(business_name)
            logger.debug(f"Sanitized business name: {sanitized_name}")
            
            # Initialize grid checker
            logger.debug("Checking DataForSEO credentials...")
            from .core.config import DataForSEOConfig
            username, password = DataForSEOConfig.get_credentials()
            if not DataForSEOConfig.validate_credentials(username, password):
                logger.error("Invalid DataForSEO credentials")
                raise ValueError("Invalid DataForSEO credentials. Please check your configuration.")
            
            # Test API connection
            logger.debug("Testing API connection...")
            if not DataForSEOConfig.test_api_connection():
                logger.error("Failed to connect to DataForSEO API")
                raise ConnectionError("Could not connect to DataForSEO API. Please check your internet connection and API status.")
            
            # Run quick check
            logger.info("Starting quick check with grid checker...")
            results = self.grid_checker.quick_check(
                business_name=sanitized_name,
                business_lat=lat,
                business_lng=lng
            )
            
            # Validate results
            if not results:
                logger.error("Quick check returned empty results")
                raise ValueError("Quick check returned empty results")
            
            if 'error' in results:
                logger.error(f"Quick check returned error: {results['error']}")
                raise ValueError(f"Quick check failed: {results['error']}")
            
            # Log results summary
            if 'results' in results and 'summary' in results['results']:
                summary = results['results']['summary']
                logger.info(f"Quick check completed - Tasks: {summary.get('total_tasks', 0)}, "
                          f"Completed: {summary.get('completed_count', 0)}, "
                          f"Failed: {summary.get('failed_count', 0)}, "
                          f"Pending: {summary.get('pending_count', 0)}")
            
            logger.info("Quick check completed successfully")
            return results
            
        except ValueError as e:
            logger.error(f"Validation error in quick check: {e}")
            raise
        except ConnectionError as e:
            logger.error(f"Connection error in quick check: {e}")
            raise
        except Exception as e:
            logger.error(f"Quick check failed with unexpected error: {e}", exc_info=True)
            raise
    
    def advanced_check(
        self,
        business_name: str,
        lat: float,
        lng: float,
        grid_size: int = 3,
        radius_km: float = 5.0,
        language_code: str = "en",
        device: str = "desktop"
    ) -> Dict[str, Any]:
        """
        Perform an advanced ranking check with custom parameters
        
        Args:
            business_name: Name of the business
            lat: Business latitude
            lng: Business longitude
            grid_size: Size of the grid (e.g., 3 for 3x3)
            radius_km: Radius in kilometers
            language_code: Language code for search
            device: Device type (desktop, mobile, tablet)
            
        Returns:
            Complete results dictionary
        """
        logger.info(f"Advanced check requested for {business_name}")
        logger.info(f"Parameters: grid={grid_size}x{grid_size}, radius={radius_km}km")
        
        try:
            # Validate inputs
            validate_business_name(business_name)
            validate_coordinates(lat, lng)
            validate_grid_parameters(grid_size, radius_km)
            
            # Run advanced check
            results = self.grid_checker.run_grid_check(
                business_name=sanitize_business_name(business_name),
                business_lat=lat,
                business_lng=lng,
                grid_size=grid_size,
                radius_km=radius_km,
                language_code=language_code,
                device=device
            )
            
            logger.info("Advanced check completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Advanced check failed: {e}")
            raise
    
    def create_tasks(
        self,
        business_name: str,
        lat: float,
        lng: float,
        grid_size: int = 3,
        radius_km: float = 5.0,
        **kwargs
    ) -> Tuple[List[str], List[str]]:
        """
        Create tasks without waiting for results
        
        Args:
            business_name: Name of the business
            lat: Business latitude
            lng: Business longitude
            grid_size: Size of the grid
            radius_km: Radius in kilometers
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (task_ids, coordinate_strings)
        """
        logger.info(f"Creating tasks for {business_name}")
        
        try:
            # Validate inputs
            validate_business_name(business_name)
            validate_coordinates(lat, lng)
            validate_grid_parameters(grid_size, radius_km)
            
            # Create tasks
            task_ids, coordinates = self.grid_checker.create_tasks_only(
                business_name=sanitize_business_name(business_name),
                business_lat=lat,
                business_lng=lng,
                grid_size=grid_size,
                radius_km=radius_km,
                **kwargs
            )
            
            logger.info(f"Created {len(task_ids)} tasks successfully")
            return task_ids, coordinates
            
        except Exception as e:
            logger.error(f"Task creation failed: {e}")
            raise
    
    def get_results(
        self,
        task_ids: List[str],
        max_wait_time: int = 1800,
        poll_interval: int = 120
    ) -> Dict[str, Any]:
        """
        Get results for existing tasks
        
        Args:
            task_ids: List of task IDs
            max_wait_time: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Results dictionary
        """
        logger.info(f"Getting results for {len(task_ids)} tasks")
        
        try:
            results = self.grid_checker.get_results_only(
                task_ids,
                max_wait_time=max_wait_time,
                poll_interval=poll_interval
            )
            
            logger.info("Results retrieved successfully")
            return results
            
        except Exception as e:
            logger.error(f"Results retrieval failed: {e}")
            raise
    
    def get_task_status(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Get current status of tasks without polling
        
        Args:
            task_ids: List of task IDs
            
        Returns:
            Status dictionary
        """
        logger.info(f"Checking status for {len(task_ids)} tasks")
        
        try:
            status = self.grid_checker.get_status(task_ids)
            
            logger.info("Status check completed")
            return status
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            raise
    
    def calculate_grid_coordinates(
        self,
        lat: float,
        lng: float,
        grid_size: int = 3,
        radius_km: float = 5.0
    ) -> List[Tuple[float, float]]:
        """
        Calculate grid coordinates without creating tasks
        
        Args:
            lat: Center latitude
            lng: Center longitude
            grid_size: Size of the grid
            radius_km: Radius in kilometers
            
        Returns:
            List of (lat, lng) coordinate tuples
        """
        logger.info(f"Calculating grid coordinates: {grid_size}x{grid_size}, {radius_km}km radius")
        
        try:
            # Validate inputs
            validate_coordinates(lat, lng)
            validate_grid_parameters(grid_size, radius_km)
            
            # Calculate coordinates
            coordinates = CoordinateCalculator.calculate_grid_coordinates(
                lat, lng, grid_size, radius_km
            )
            
            logger.info(f"Generated {len(coordinates)} grid points")
            return coordinates
            
        except Exception as e:
            logger.error(f"Grid calculation failed: {e}")
            raise
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information and status
        
        Returns:
            Service information dictionary
        """
        from .core.config import DataForSEOConfig
        
        try:
            username, password = DataForSEOConfig.get_credentials()
            credentials_valid = DataForSEOConfig.validate_credentials(username, password)
            api_working = DataForSEOConfig.test_api_connection()
            
            return {
                'service': 'Local Ranking Grid Service',
                'version': '2.0.0',
                'status': 'active',
                'credentials_configured': credentials_valid,
                'api_connection': 'working' if api_working else 'not working',
                'features': {
                    'quick_check': '3x3 grid, 5km radius',
                    'advanced_check': 'Custom grid and radius',
                    'split_workflow': 'Separate task creation and result fetching',
                    'grid_calculation': 'Coordinate grid generation'
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Service info check failed: {e}")
            return {
                'service': 'Local Ranking Grid Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    # === Rank extraction helpers ===
    @staticmethod
    def _extract_domain(url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return ""

    @staticmethod
    def compute_rank_for_domain(task_result: Dict[str, Any], target_domain: str) -> Optional[int]:
        """
        Given a single task's API response and a target domain, return the 1-based rank
        position where the domain appears, or None if not found.
        """
        if not task_result or not target_domain:
            return None
        target_domain = target_domain.lower()
        try:
            tasks = task_result.get('tasks', [])
            if not tasks:
                return None
            first_task = tasks[0]
            results = first_task.get('result', [])
            if not results:
                return None
            items = results[0].get('items', [])
            for index, item in enumerate(items, start=1):
                item_domain = (
                    item.get('domain')
                    or RankingService._extract_domain(item.get('url', ''))
                    or RankingService._extract_domain(item.get('source_url', ''))
                )
                if item_domain and target_domain in item_domain:
                    return index
            return None
        except Exception:
            return None

    @staticmethod
    def compute_ranks_for_results(completed_results: Dict[str, Any], target_domain: str) -> Dict[str, Optional[int]]:
        """
        Given a mapping of task_id -> completed result, compute rank for each using compute_rank_for_domain.
        Returns mapping task_id -> rank (or None).
        """
        ranks: Dict[str, Optional[int]] = {}
        if not completed_results or not target_domain:
            return ranks
        for task_id, task_result in completed_results.items():
            ranks[task_id] = RankingService.compute_rank_for_domain(task_result, target_domain)
        return ranks

    @staticmethod
    def build_rank_map(task_ids: List[str], coordinate_strings: List[str], results: Dict[str, Any], target_domain: Optional[str]) -> List[Dict[str, Any]]:
        """
        Build an ordered rank map tying each coordinate to its task_id and computed rank.
        coordinate_strings are in "lat,lng,zoom" format in the same order as task_ids.
        results is the structure returned by GridRankChecker.get_results_only().
        """
        if not task_ids or not coordinate_strings or not results:
            return []

        completed = results.get('completed', {})
        failed = results.get('failed', {})
        ranks_by_task: Dict[str, Optional[int]] = {}
        if target_domain:
            ranks_by_task = RankingService.compute_ranks_for_results(completed, target_domain)

        def parse_coord(coord: str) -> Tuple[float, float, int]:
            try:
                parts = coord.split(',')
                lat = float(parts[0])
                lng = float(parts[1])
                zoom = int(parts[2]) if len(parts) > 2 else 15
                return lat, lng, zoom
            except Exception:
                return 0.0, 0.0, 15

        rank_map: List[Dict[str, Any]] = []
        for idx, (tid, coord_str) in enumerate(zip(task_ids, coordinate_strings)):
            lat, lng, zoom = parse_coord(coord_str)
            status = 'pending'
            if tid in completed:
                status = 'completed'
            elif tid in failed:
                status = 'failed'
            rank_value = ranks_by_task.get(tid) if target_domain else None
            rank_map.append({
                'index': idx,
                'task_id': tid,
                'lat': lat,
                'lng': lng,
                'zoom': zoom,
                'status': status,
                'rank': rank_value,
            })

        return rank_map
