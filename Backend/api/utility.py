from datetime import timedelta

from django.conf import settings

# ============================================================
# Utilities
# ============================================================


def get_weather_cache_expiry_delta():
    """
    Centralized cache expiry logic to avoid duplication
    and ensure consistency across the application.
    """
    return timedelta(minutes=getattr(settings, "WEATHER_CACHE_MINUTES", 60))
