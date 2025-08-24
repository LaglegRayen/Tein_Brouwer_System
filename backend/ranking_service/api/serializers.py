"""
Django REST Framework serializers for the ranking service API
"""

from rest_framework import serializers


class GridRankRequestSerializer(serializers.Serializer):
    """
    Serializer for grid rank check requests
    """
    business_name = serializers.CharField(
        max_length=200,
        help_text="Name of the business to search for"
    )
    business_lat = serializers.FloatField(
        min_value=-90.0,
        max_value=90.0,
        help_text="Business latitude"
    )
    business_lng = serializers.FloatField(
        min_value=-180.0,
        max_value=180.0,
        help_text="Business longitude"
    )
    grid_size = serializers.IntegerField(
        min_value=1,
        max_value=10,
        default=3,
        help_text="Size of the grid (e.g., 3 for 3x3 grid)"
    )
    radius_km = serializers.FloatField(
        min_value=0.1,
        max_value=50.0,
        default=5.0,
        help_text="Radius in kilometers for the grid"
    )
    language_code = serializers.CharField(
        max_length=5,
        default="en",
        help_text="Language code for search"
    )
    device = serializers.ChoiceField(
        choices=['desktop', 'mobile', 'tablet'],
        default='desktop',
        help_text="Device type for search"
    )
    zoom = serializers.IntegerField(
        min_value=1,
        max_value=20,
        default=15,
        help_text="Map zoom level"
    )


class TaskCreationRequestSerializer(serializers.Serializer):
    """
    Serializer for task creation requests (create tasks only)
    """
    business_name = serializers.CharField(max_length=200)
    business_lat = serializers.FloatField(min_value=-90.0, max_value=90.0)
    business_lng = serializers.FloatField(min_value=-180.0, max_value=180.0)
    grid_size = serializers.IntegerField(min_value=1, max_value=10, default=3)
    radius_km = serializers.FloatField(min_value=0.1, max_value=50.0, default=5.0)
    language_code = serializers.CharField(max_length=5, default="en")
    device = serializers.ChoiceField(choices=['desktop', 'mobile', 'tablet'], default='desktop')
    zoom = serializers.IntegerField(min_value=1, max_value=20, default=15)


class ResultsRequestSerializer(serializers.Serializer):
    """
    Serializer for results retrieval requests
    """
    task_ids = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of task IDs to fetch results for"
    )
    max_wait_time = serializers.IntegerField(
        min_value=60,
        max_value=3600,
        default=1800,
        help_text="Maximum time to wait in seconds"
    )
    poll_interval = serializers.IntegerField(
        min_value=30,
        max_value=600,
        default=120,
        help_text="Polling interval in seconds"
    )


class StatusRequestSerializer(serializers.Serializer):
    """
    Serializer for status check requests
    """
    task_ids = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of task IDs to check status for"
    )


class CoordinateSerializer(serializers.Serializer):
    """
    Serializer for coordinate data
    """
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class GridParametersSerializer(serializers.Serializer):
    """
    Serializer for grid parameters
    """
    size = serializers.IntegerField()
    radius_km = serializers.FloatField()


class TaskSummarySerializer(serializers.Serializer):
    """
    Serializer for task summary data
    """
    total_tasks = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    polls_performed = serializers.IntegerField(required=False)
    elapsed_time_seconds = serializers.FloatField(required=False)


class MetadataSerializer(serializers.Serializer):
    """
    Serializer for operation metadata
    """
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    total_duration_seconds = serializers.FloatField()
    success = serializers.BooleanField()


class GridRankResponseSerializer(serializers.Serializer):
    """
    Serializer for grid rank check responses
    """
    business_name = serializers.CharField()
    center_coordinates = CoordinateSerializer()
    grid_parameters = GridParametersSerializer()
    grid_coordinates = serializers.ListField(child=serializers.CharField())
    task_ids = serializers.ListField(child=serializers.CharField())
    results = serializers.DictField()
    metadata = MetadataSerializer()
    error = serializers.CharField(required=False)


class TaskCreationResponseSerializer(serializers.Serializer):
    """
    Serializer for task creation responses
    """
    task_ids = serializers.ListField(child=serializers.CharField())
    coordinates = serializers.ListField(child=serializers.CharField())
    business_name = serializers.CharField()
    center_coordinates = CoordinateSerializer()
    grid_parameters = GridParametersSerializer()
    timestamp = serializers.DateTimeField()


class StatusResponseSerializer(serializers.Serializer):
    """
    Serializer for status check responses
    """
    status = serializers.CharField()
    task_count = serializers.IntegerField(required=False)
    task_status = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()
    error = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
