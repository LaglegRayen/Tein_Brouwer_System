"""
Local Ranking Grid Service

A comprehensive Django-integrated service for grid-based local ranking analysis.
This service provides modular components for:
- Coordinate grid calculations around business locations
- Batch task creation and management with DataForSEO API
- Result polling and analysis
- Django REST API endpoints for frontend integration

Components:
- core/: Main business logic modules
- utils/: Utility functions and helpers
- api/: Django views and serializers
"""

from .core.grid_rank_checker import GridRankChecker
from .core.coordinate_calculator import CoordinateCalculator
from .core.task_batcher import TaskBatcher
from .core.results_fetcher import ResultsFetcher

__all__ = [
    'GridRankChecker',
    'CoordinateCalculator', 
    'TaskBatcher',
    'ResultsFetcher'
]

__version__ = "2.0.0"
