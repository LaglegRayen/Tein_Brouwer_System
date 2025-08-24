from django.apps import AppConfig


class RankingServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ranking_service'
    verbose_name = 'Local Ranking Grid Service'
    
    def ready(self):
        """
        Application startup hook
        """
        # Import any necessary startup code here
        pass
