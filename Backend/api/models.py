from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# --- Manager for Efficient Querying ---

class WeatherCacheManager(models.Manager):
    def get_valid_cache(self, city_name, state_name, country):
        """
        Custom manager method to find a valid (unexpired) cache entry.
        """
        threshold = getattr(settings, 'WEATHER_CACHE_MINUTES', 60)
        expiry_limit = timezone.now() - timedelta(minutes=threshold)
        
        query = self.filter(city__iexact=city_name, updated_at__gte=expiry_limit)
        if state_name:
            query = query.filter(state__iexact=state_name)
        if country:
            query = query.filter(country__iexact=country)  
        return query.first()

# --- Models ---

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email Address')
    phone = models.CharField(
        max_length=15, 
        unique=True, 
        verbose_name='Phone Number'
    )
    
    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return self.username


class WeatherCache(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    data = models.JSONField(help_text="Full payload from provider")
    updated_at = models.DateTimeField(auto_now=True)

    objects = WeatherCacheManager()

    class Meta:
        # Composite Index: Most searches will be City + Country
        indexes = [
            models.Index(fields=['city', 'state', 'country'], name='city_country_idx'),
        ]
        # Prevents duplicate rows for the same city/country
        unique_together = ('city', 'state', 'country')
        verbose_name = "Weather Cache"  
        verbose_name_plural = "Weather Cache"


    @property
    def is_valid(self):
        threshold = getattr(settings, 'WEATHER_CACHE_MINUTES', 60)
        return self.updated_at >= timezone.now() - timedelta(minutes=threshold)

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"


class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='search_history'
    )
    # Linked to cache so we don't duplicate JSON data in two tables
    response_data = models.JSONField(help_text="The weather data returned to the user for this search.")
    # Keep city name here as a backup in case the Cache entry is deleted
    city_name_queried = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True) # Updates time if user searches same city again

    class Meta:
        ordering = ['-timestamp']
        # Ensures a user doesn't have 100 identical rows for the same city
        unique_together = ('user', 'city_name_queried')

    def __str__(self):
        return f"{self.user.username} -> {self.city_name_queried}"