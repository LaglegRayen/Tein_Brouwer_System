from django.conf import settings
from django.db import models


class RankingJob(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ranking_jobs",
    )
    business_name = models.CharField(max_length=255)
    center_lat = models.FloatField()
    center_lng = models.FloatField()
    grid_size = models.PositiveIntegerField(default=3)
    radius_km = models.FloatField(default=5.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"RankingJob({self.business_name}, {self.center_lat},{self.center_lng})"


class RankingTask(models.Model):
    job = models.ForeignKey(
        RankingJob,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    dataforseo_task_id = models.CharField(max_length=128, unique=True)
    coord_lat = models.FloatField()
    coord_lng = models.FloatField()
    coord_zoom = models.PositiveIntegerField(default=15)
    status = models.CharField(max_length=64, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    raw_result = models.JSONField(null=True, blank=True)
    target_domain = models.CharField(max_length=255, null=True, blank=True)
    rank_position = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Task({self.dataforseo_task_id})"


