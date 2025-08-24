import requests
import json
import time
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class ResultsFetcher:
    """
    Handles fetching results from DataForSEO tasks with async polling
    Enhanced with comprehensive logging and error handling
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
        self.base_url = "https://api.dataforseo.com/v3/serp/google/maps/task_get/advanced"
        self.auth = (username, password)
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        logger.info(f"ResultsFetcher initialized for user: {username}")
    
    def fetch_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch result for a single task
        
        Args:
            task_id: Task ID to fetch results for
            
        Returns:
            Task result or None if not ready/failed
        """
        logger.debug(f"Fetching result for task: {task_id}")
        
        try:
            url = f"{self.base_url}/{task_id}"
            logger.debug(f"GET URL: {url}")
            
            response = requests.get(
                url,
                auth=self.auth,
                timeout=30
            )
            
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()
            
            api_response = response.json()
            logger.debug(f"Got response for task {task_id}")
            
            # Debug the task status
            if "tasks" in api_response and api_response["tasks"]:
                task_data = api_response["tasks"][0]
                status_code = task_data.get("status_code", "N/A")
                status_message = task_data.get("status_message", "N/A")
                result_count = task_data.get("result_count", 0)
                logger.debug(f"Task {task_id} - Status: {status_code} ({status_message}), Results: {result_count}")
            
            return api_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for task {task_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode failed for task {task_id}: {e}")
            logger.error(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
            return None
    
    def is_task_completed(self, task_result: Dict[str, Any]) -> bool:
        """
        Check if a task is completed successfully
        
        Args:
            task_result: API response for the task
            
        Returns:
            True if task is completed with results
        """
        if not task_result or "tasks" not in task_result:
            return False
        
        for task in task_result["tasks"]:
            if task.get("status_code") == 20000 and task.get("result_count", 0) > 0:
                return True
        
        return False
    
    def is_task_failed(self, task_result: Dict[str, Any]) -> bool:
        """
        Check if a task has failed
        
        Args:
            task_result: API response for the task
            
        Returns:
            True if task has failed
        """
        if not task_result or "tasks" not in task_result:
            return True
        
        for task in task_result["tasks"]:
            status_code = task.get("status_code", 0)
            # Status codes indicating failure or final non-success states
            if status_code in [40000, 40100, 40200, 40300, 50000]:
                return True
        
        return False
    
    def poll_task_results(self, task_ids: List[str], max_wait_time: int = 1800,
                         poll_interval: int = 120) -> Dict[str, Any]:
        """
        Poll for task results with configurable intervals
        
        Args:
            task_ids: List of task IDs to poll
            max_wait_time: Maximum time to wait in seconds (default 30 min)
            poll_interval: Polling interval in seconds (default 2 min)
            
        Returns:
            Dictionary with completed and failed task results
        """
        pending_tasks = set(task_ids)
        completed_results = {}
        failed_results = {}
        
        start_time = datetime.now()
        max_end_time = start_time + timedelta(seconds=max_wait_time)
        
        logger.info(f"Starting to poll {len(pending_tasks)} tasks...")
        logger.info(f"Will poll every {poll_interval} seconds for up to {max_wait_time} seconds")
        
        poll_count = 0
        
        while pending_tasks and datetime.now() < max_end_time:
            poll_count += 1
            current_batch = list(pending_tasks)
            
            logger.info(f"--- Poll #{poll_count}: Checking {len(current_batch)} pending tasks at {datetime.now().strftime('%H:%M:%S')} ---")
            
            for task_id in current_batch:
                if task_id in self.completed_tasks or task_id in self.failed_tasks:
                    pending_tasks.discard(task_id)
                    continue
                
                logger.debug(f"Checking task: {task_id}")
                result = self.fetch_task_result(task_id)
                
                if result:
                    if self.is_task_completed(result):
                        logger.info(f"✅ Task {task_id} completed successfully")
                        completed_results[task_id] = result
                        self.completed_tasks.add(task_id)
                        pending_tasks.discard(task_id)
                    
                    elif self.is_task_failed(result):
                        logger.warning(f"❌ Task {task_id} failed")
                        failed_results[task_id] = result
                        self.failed_tasks.add(task_id)
                        pending_tasks.discard(task_id)
                    
                    else:
                        logger.debug(f"⏳ Task {task_id} still processing...")
                else:
                    logger.warning(f"⚠️ Could not fetch result for task {task_id}")
            
            if pending_tasks:
                remaining_time = (max_end_time - datetime.now()).total_seconds()
                if remaining_time > poll_interval:
                    logger.info(f"💤 Waiting {poll_interval} seconds before next poll...")
                    logger.info(f"   Remaining tasks: {len(pending_tasks)}")
                    logger.info(f"   Time remaining: {int(remaining_time)} seconds")
                    time.sleep(poll_interval)
                else:
                    logger.info(f"⏰ Not enough time remaining for another poll cycle")
                    break
        
        # Final status
        logger.info(f"=== Final Results ===")
        logger.info(f"✅ Completed: {len(completed_results)} tasks")
        logger.info(f"❌ Failed: {len(failed_results)} tasks")
        logger.info(f"⏳ Still pending: {len(pending_tasks)} tasks")
        logger.info(f"🔄 Total polls performed: {poll_count}")
        
        return {
            "completed": completed_results,
            "failed": failed_results,
            "pending": list(pending_tasks),
            "summary": {
                "total_tasks": len(task_ids),
                "completed_count": len(completed_results),
                "failed_count": len(failed_results),
                "pending_count": len(pending_tasks),
                "polls_performed": poll_count,
                "elapsed_time_seconds": (datetime.now() - start_time).total_seconds()
            }
        }
    
    def get_all_results(self, task_ids: List[str], **kwargs) -> Dict[str, Any]:
        """
        Convenience method to get all results for a list of task IDs
        
        Args:
            task_ids: List of task IDs
            **kwargs: Additional parameters for polling
            
        Returns:
            All results organized by status
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
                    "pending_count": 0,
                    "polls_performed": 0,
                    "elapsed_time_seconds": 0
                }
            }
        
        logger.info(f"Getting all results for {len(task_ids)} tasks")
        return self.poll_task_results(task_ids, **kwargs)
    
    def get_quick_status(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Get quick status check without polling
        
        Args:
            task_ids: List of task IDs
            
        Returns:
            Current status of all tasks
        """
        if not task_ids:
            return {"completed": 0, "failed": 0, "pending": 0, "unknown": 0}
        
        logger.info(f"Performing quick status check for {len(task_ids)} tasks")
        
        completed = 0
        failed = 0
        pending = 0
        unknown = 0
        
        for task_id in task_ids:
            result = self.fetch_task_result(task_id)
            
            if result:
                if self.is_task_completed(result):
                    completed += 1
                elif self.is_task_failed(result):
                    failed += 1
                else:
                    pending += 1
            else:
                unknown += 1
        
        status = {
            "completed": completed,
            "failed": failed, 
            "pending": pending,
            "unknown": unknown,
            "total": len(task_ids)
        }
        
        logger.info(f"Quick status: {status}")
        return status
