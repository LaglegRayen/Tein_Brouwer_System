"""Test the complete service flow using our actual service classes"""
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

from ranking_service.core.grid_rank_checker import GridRankChecker
from ranking_service.core.coordinate_calculator import CoordinateCalculator
from ranking_service.utils.logging_config import get_logger
from ranking_service.models import RankingJob, RankingTask
from ranking_service.service import RankingService
from django.contrib.auth import get_user_model
from django.utils import timezone
from urllib.parse import urlparse

logger = get_logger(__name__)


def test_service_flow():
    """Test the complete flow using our service classes (no direct HTTP calls here)."""
    try:
        # Get credentials first
        logger.info("Getting DataForSEO credentials...")
        from ranking_service.core.config import DataForSEOConfig
        username, password = DataForSEOConfig.get_credentials()
        if not username or not password:
            logger.error("Failed to get credentials")
            return

        # Initialize orchestrator
        logger.info("Initializing GridRankChecker...")
        grid_checker = GridRankChecker(username=username, password=password)

        # Test business details
        business_name = "test restaurant"
        business_lat = 36.8301732
        business_lng = 10.0949113
        radius_km = 5.0
        grid_size = 3

        # Step 1: Calculate grid coordinates using our calculator
        logger.info("\n=== Testing Coordinate Calculator ===")
        logger.info(f"Calculating {grid_size}x{grid_size} grid with {radius_km}km radius")
        grid_points = CoordinateCalculator.calculate_grid_coordinates(
            center_lat=business_lat,
            center_lng=business_lng,
            grid_size=grid_size,
            radius_km=radius_km
        )
        logger.info(f"Generated {len(grid_points)} grid points")
        for point in grid_points:
            logger.info(f"Point: {point}")

        # Create a DB job linked to first user (adjust as needed)
        logger.info("\n=== Creating RankingJob in DB ===")
        User = get_user_model()
        job_user = User.objects.first()
        target_domain = os.getenv("TARGET_DOMAIN")  # optional, e.g. example.com
        job = RankingJob.objects.create(
            user=job_user,
            business_name=business_name,
            center_lat=business_lat,
            center_lng=business_lng,
            grid_size=grid_size,
            radius_km=radius_km,
        )
        logger.info(f"Created job id={job.id} for user={job_user}")

        # Step 2: Create tasks using GridRankChecker (TaskBatcher under the hood) and persist to DB
        logger.info("\n=== Creating tasks via GridRankChecker.create_tasks_only and persisting ===")
        task_ids, coordinate_strings = grid_checker.create_tasks_only(
            business_name=business_name,
            business_lat=business_lat,
            business_lng=business_lng,
            grid_size=grid_size,
            radius_km=radius_km,
            language_code="en",
            device="desktop"
        )

        if not task_ids:
            logger.error("No tasks were created successfully")
            return

        logger.info(f"Created {len(task_ids)} tasks; persisting to DB")

        # Helper to parse "lat,lng,zoom"
        def parse_coord_str(coord_str: str):
            try:
                parts = coord_str.split(",")
                lat_v = float(parts[0])
                lng_v = float(parts[1])
                zoom_v = int(parts[2]) if len(parts) > 2 else 15
                return lat_v, lng_v, zoom_v
            except Exception:
                return None, None, 15

        persisted_tasks = []
        for task_id, coord_str in zip(task_ids, coordinate_strings):
            lat_v, lng_v, zoom_v = parse_coord_str(coord_str)
            rt = RankingTask.objects.create(
                job=job,
                dataforseo_task_id=task_id,
                coord_lat=lat_v if lat_v is not None else 0.0,
                coord_lng=lng_v if lng_v is not None else 0.0,
                coord_zoom=zoom_v,
                status="pending",
                target_domain=target_domain,
            )
            persisted_tasks.append(rt)
        logger.info(f"Persisted {len(persisted_tasks)} RankingTask rows")

        # Step 3: Poll for results using GridRankChecker.get_results_only (which uses ResultsFetcher)
        logger.info("\n=== Testing Results Fetching via GridRankChecker.get_results_only ===")
        results = grid_checker.get_results_only(
            task_ids=task_ids,
            max_wait_time=3600,       # 10 minutes total
            poll_interval=120        # poll every 2 minutes
        )

        # Compute rank per coordinate for target_domain and persist raw results using service helpers
        # Build a dict task_id -> completed result for convenience
        completed = results.get("completed", {})
        failed = results.get("failed", {})
        pending_ids = set(results.get("pending", []))

        ranks_by_task = {}
        if target_domain:
            ranks_by_task = RankingService.compute_ranks_for_results(completed, target_domain)

        for rt in RankingTask.objects.filter(job=job):
            tid = rt.dataforseo_task_id
            if tid in completed:
                rt.raw_result = completed[tid]
                rt.status = "completed"
                rt.completed_at = timezone.now()
                if rt.target_domain and tid in ranks_by_task:
                    rt.rank_position = ranks_by_task.get(tid)
                rt.save(update_fields=["raw_result", "status", "completed_at", "rank_position"])
            elif tid in failed:
                rt.raw_result = failed[tid]
                rt.status = "failed"
                rt.completed_at = timezone.now()
                rt.save(update_fields=["raw_result", "status", "completed_at"])
            elif tid in pending_ids:
                rt.status = "pending"
                rt.save(update_fields=["status"])

        summary = results.get("summary", {})
        logger.info(f"Saved results to DB. Summary: {summary}")
        if target_domain:
            sample = list(
                RankingTask.objects.filter(job=job, status="completed")
                .values("coord_lat", "coord_lng", "rank_position")[:9]
            )
            logger.info(f"Sample ranks for {target_domain}: {sample}")

    except Exception as e:
        logger.error(f"Error in service flow: {e}", exc_info=True)


if __name__ == '__main__':
    test_service_flow()