"""
Django REST Framework views for the ranking service API
"""

import logging
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch

from ..service import RankingService
from ..utils.logging_config import get_logger
from ..models import RankingJob, RankingTask
from .serializers import (
    GridRankRequestSerializer,
    TaskCreationRequestSerializer,
    ResultsRequestSerializer,
    StatusRequestSerializer,
    GridRankResponseSerializer,
    TaskCreationResponseSerializer,
    StatusResponseSerializer
)

logger = get_logger(__name__)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def run_grid_check(request):
    """
    Complete grid rank check workflow: create tasks and wait for results
    
    POST /api/ranking/grid-check/
    """
    logger.info(f"Grid check request from user: {request.user.username}")
    
    # Validate request data
    serializer = GridRankRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"Invalid request data: {serializer.errors}")
        return Response({
            'error': 'Invalid request data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        # Initialize RankingService
        service = RankingService()
        
        # Run advanced check
        results = service.advanced_check(**validated_data)

        # Optional rank map: if client supplies target_domain, compute a rank map
        target_domain = request.data.get('target_domain')
        if target_domain and 'task_ids' in results and 'grid_coordinates' in results and 'results' in results:
            rank_map = service.build_rank_map(
                task_ids=results.get('task_ids', []),
                coordinate_strings=results.get('grid_coordinates', []),
                results=results.get('results', {}),
                target_domain=target_domain
            )
            results['rank_map'] = rank_map
        
        # Serialize response
        response_serializer = GridRankResponseSerializer(data=results)
        if response_serializer.is_valid():
            logger.info(f"Grid check completed successfully for user: {request.user.username}")
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        else:
            logger.error(f"Response serialization failed: {response_serializer.errors}")
            return Response(results, status=status.HTTP_200_OK)  # Return raw data
        
    except Exception as e:
        logger.error(f"Grid check failed: {e}")
        return Response({
            'error': 'Grid check failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_tasks(request):
    """
    Create tasks only (without waiting for results)
    
    POST /api/ranking/create-tasks/
    """
    logger.info(f"Create tasks request from user: {request.user.username}")
    
    # Validate request data
    serializer = TaskCreationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"Invalid request data: {serializer.errors}")
        return Response({
            'error': 'Invalid request data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        # Initialize RankingService
        service = RankingService()
        
        # Create tasks only
        task_ids, coordinates = service.create_tasks(**validated_data)
        
        # Prepare response
        response_data = {
            'task_ids': task_ids,
            'coordinates': coordinates,
            'business_name': validated_data['business_name'],
            'center_coordinates': {
                'lat': validated_data['business_lat'],
                'lng': validated_data['business_lng']
            },
            'grid_parameters': {
                'size': validated_data['grid_size'],
                'radius_km': validated_data['radius_km']
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Tasks created successfully for user: {request.user.username}, task count: {len(task_ids)}")
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Task creation failed: {e}")
        return Response({
            'error': 'Task creation failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_results(request):
    """
    Get results for existing task IDs
    
    POST /api/ranking/get-results/
    """
    logger.info(f"Get results request from user: {request.user.username}")
    
    # Validate request data
    serializer = ResultsRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"Invalid request data: {serializer.errors}")
        return Response({
            'error': 'Invalid request data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        # Initialize RankingService
        service = RankingService()
        
        # Get results
        results = service.get_results(**validated_data)
        
        logger.info(f"Results retrieved successfully for user: {request.user.username}")
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Results retrieval failed: {e}")
        return Response({
            'error': 'Results retrieval failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_status(request):
    """
    Get quick status check for task IDs
    
    POST /api/ranking/status/
    """
    logger.info(f"Status check request from user: {request.user.username}")
    
    # Validate request data
    serializer = StatusRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"Invalid request data: {serializer.errors}")
        return Response({
            'error': 'Invalid request data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        # Initialize RankingService
        service = RankingService()
        
        # Get status
        status_result = service.get_task_status(validated_data['task_ids'])
        
        logger.info(f"Status check completed for user: {request.user.username}")
        return Response(status_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return Response({
            'error': 'Status check failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def service_info(request):
    """
    Get service information and health check
    
    GET /api/ranking/info/
    """
    logger.info(f"Service info request from user: {request.user.username}")
    
    try:
        # Initialize RankingService
        service = RankingService()
        
        # Get service info
        info = service.get_service_info()
        
        # Add API endpoints
        info['endpoints'] = {
            'complete_check': '/api/ranking/grid-check/',
            'create_tasks': '/api/ranking/create-tasks/',
            'get_results': '/api/ranking/get-results/',
            'status_check': '/api/ranking/status/',
            'service_info': '/api/ranking/info/'
        }
        
        return Response(info, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Service info failed: {e}")
        return Response({
            'error': 'Service info failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def quick_check(request):
    """
    Quick grid check with default parameters (3x3 grid, 5km radius)
    
    POST /api/ranking/quick-check/
    """
    # Log request details
    logger.info("=== Quick Check Request Details ===")
    logger.info(f"User: {request.user}")
    logger.info(f"Authenticated: {request.user.is_authenticated}")
    logger.info(f"Username: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    logger.info(f"Session ID: {request.session.session_key}")
    logger.info(f"Method: {request.method}")
    logger.info("Headers:")
    for key, value in request.headers.items():
        logger.info(f"  {key}: {value}")
    logger.info("Data:")
    logger.info(f"  {request.data}")
    logger.info("Cookies:")
    for key, value in request.COOKIES.items():
        logger.info(f"  {key}: {value}")
    logger.info("Session data:")
    for key, value in request.session.items():
        logger.info(f"  {key}: {value}")
    
    # Verify authentication
    if not request.user.is_authenticated:
        logger.warning("Request rejected: User not authenticated")
        return Response({
            'error': 'Authentication required',
            'detail': 'Please log in to use this service'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Simple validation for required fields only
    required_fields = ['business_name', 'business_lat', 'business_lng']
    if not all(field in request.data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in request.data]
        logger.warning(f"Missing required fields: {missing_fields}")
        return Response({
            'error': 'Missing required fields',
            'required': required_fields,
            'missing': missing_fields
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Initialize RankingService
        service = RankingService()
        
        # Run quick check
        results = service.quick_check(
            business_name=request.data['business_name'],
            lat=float(request.data['business_lat']),
            lng=float(request.data['business_lng'])
        )

        # Optional rank map
        target_domain = request.data.get('target_domain')
        if target_domain and 'task_ids' in results and 'grid_coordinates' in results and 'results' in results:
            rank_map = service.build_rank_map(
                task_ids=results.get('task_ids', []),
                coordinate_strings=results.get('grid_coordinates', []),
                results=results.get('results', {}),
                target_domain=target_domain
            )
            results['rank_map'] = rank_map
        
        logger.info(f"Quick check completed for user: {request.user.username}")
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Quick check failed: {e}")
        return Response({
            'error': 'Quick check failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def history(request):
    """
    Return recent saved rank grids filtered by business_name (optional) for the current user.
    GET /api/ranking/history/?business_name=foo
    """
    try:
        business_name = request.query_params.get('business_name')
        user = request.user

        qs = RankingJob.objects.filter(user=user).order_by('-created_at')
        if business_name:
            qs = qs.filter(business_name__icontains=business_name)

        jobs = qs[:5]
        payload = []
        for job in jobs:
            # Order tasks to form a stable grid: top->bottom (lat desc), left->right (lng asc)
            tasks = RankingTask.objects.filter(job=job).order_by('-coord_lat', 'coord_lng')
            # Build a simple rank_map from saved rows
            rank_map = []
            detected_domain = None
            for t in tasks:
                rank_map.append({
                    'task_id': t.dataforseo_task_id,
                    'lat': t.coord_lat,
                    'lng': t.coord_lng,
                    'zoom': t.coord_zoom,
                    'status': t.status,
                    'rank': t.rank_position,
                })
                if not detected_domain and t.target_domain:
                    detected_domain = t.target_domain

            payload.append({
                'job_id': job.id,
                'business_name': job.business_name,
                'center_coordinates': {'lat': job.center_lat, 'lng': job.center_lng},
                'grid_parameters': {'size': job.grid_size, 'radius_km': job.radius_km},
                'created_at': job.created_at.isoformat(),
                'target_domain': detected_domain,
                'rank_map': rank_map,
            })

        return Response({'results': payload}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"History fetch failed: {e}")
        return Response({'error': 'History fetch failed', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
