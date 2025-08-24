import math
import logging
from typing import List, Tuple

from ..utils.logging_config import get_logger
from ..utils.validators import validate_coordinates, validate_grid_parameters

logger = get_logger(__name__)


class CoordinateCalculator:
    """
    Calculates grid coordinates around a business location for ranking checks
    Enhanced with logging and validation
    """
    
    @staticmethod
    def calculate_grid_coordinates(center_lat: float, center_lng: float, 
                                 grid_size: int = 3, radius_km: float = 5.0) -> List[Tuple[float, float]]:
        """
        Calculate grid coordinates around a center point
        
        Args:
            center_lat: Center latitude
            center_lng: Center longitude
            grid_size: Size of the grid (e.g., 3 for 3x3 grid)
            radius_km: Radius in kilometers for the grid
            
        Returns:
            List of (lat, lng) tuples
            
        Raises:
            ValueError: If coordinates or grid parameters are invalid
        """
        logger.debug(f"Calculating grid coordinates for center: {center_lat}, {center_lng}")
        logger.debug(f"Grid parameters - size: {grid_size}, radius: {radius_km}km")
        
        # Validate inputs
        validate_coordinates(center_lat, center_lng)
        validate_grid_parameters(grid_size, radius_km)
        
        coordinates = []
        
        # Convert radius from km to degrees (approximate)
        lat_degree_km = 111.0  # 1 degree latitude ≈ 111 km
        lng_degree_km = 111.0 * math.cos(math.radians(center_lat))  # Longitude varies by latitude
        
        lat_offset = radius_km / lat_degree_km
        lng_offset = radius_km / lng_degree_km
        
        # Calculate grid points
        step_size = 2.0 / (grid_size - 1) if grid_size > 1 else 0
        
        for i in range(grid_size):
            for j in range(grid_size):
                # Calculate relative position (-1 to 1)
                lat_factor = -1 + i * step_size if grid_size > 1 else 0
                lng_factor = -1 + j * step_size if grid_size > 1 else 0
                
                # Calculate actual coordinates
                lat = center_lat + (lat_factor * lat_offset)
                lng = center_lng + (lng_factor * lng_offset)
                
                coordinates.append((lat, lng))
        
        logger.info(f"Generated {len(coordinates)} grid coordinates")
        return coordinates
    
    @staticmethod
    def format_coordinate_for_api(lat: float, lng: float, zoom: int = 15) -> str:
        """
        Format coordinates for DataForSEO API
        
        Args:
            lat: Latitude
            lng: Longitude
            zoom: Zoom level for the search
            
        Returns:
            Formatted coordinate string for API
        """
        validate_coordinates(lat, lng)
        if not (1 <= zoom <= 20):
            raise ValueError(f"Zoom level must be between 1 and 20, got {zoom}")
            
        formatted = f"{lat:.6f},{lng:.6f},{zoom}"
        logger.debug(f"Formatted coordinate: {formatted}")
        return formatted
    
    @staticmethod
    def generate_task_coordinates(business_lat: float, business_lng: float,
                                grid_size: int = 3, radius_km: float = 5.0,
                                zoom: int = 15) -> List[str]:
        """
        Generate all coordinate strings for task creation
        
        Args:
            business_lat: Business latitude
            business_lng: Business longitude
            grid_size: Grid size for checking
            radius_km: Radius around business
            zoom: Map zoom level
            
        Returns:
            List of formatted coordinate strings for API
        """
        logger.info(f"Generating task coordinates for business at {business_lat}, {business_lng}")
        
        grid_coords = CoordinateCalculator.calculate_grid_coordinates(
            business_lat, business_lng, grid_size, radius_km
        )
        
        coordinates = [
            CoordinateCalculator.format_coordinate_for_api(lat, lng, zoom)
            for lat, lng in grid_coords
        ]
        
        logger.info(f"Generated {len(coordinates)} task coordinates")
        return coordinates
