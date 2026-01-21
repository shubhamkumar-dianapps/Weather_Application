from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone
from api.utility import get_weather_cache_expiry_delta


# ============================================================
# Custom User Model
# ============================================================


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser
    with email and phone number enforcement.
    """

    email = models.EmailField(unique=True, verbose_name="Email Address")

    phone = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Phone Number",
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format '+999999999'.",
            )
        ],
    )

    REQUIRED_FIELDS = ["email", "phone"]

    def __str__(self) -> str:
        return self.username


# ============================================================
# Weather Cache
# ============================================================


class WeatherCacheManager(models.Manager):
    """
    Custom manager to fetch only valid (non-expired) cache entries.
    """

    def get_valid_cache(
        self, city: str, state: str | None = None, country: str | None = None
    ):
        expiry_limit = timezone.now() - get_weather_cache_expiry_delta()

        filters = {"city__iexact": city, "updated_at__gte": expiry_limit}

        if state:
            filters["state__iexact"] = state
        if country:
            filters["country__iexact"] = country

        return self.filter(**filters).first()


class WeatherCache(models.Model):
    """
    Stores raw weather API responses to avoid repeated external calls.
    JSONField is intentionally used because the provider schema
    may change over time.
    """

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, validators=[MinLengthValidator(2)])

    data = models.JSONField(help_text="Raw weather provider response payload")

    updated_at = models.DateTimeField(auto_now=True)

    objects = WeatherCacheManager()

    class Meta:
        verbose_name = "Weather Cache"
        verbose_name_plural = "Weather Cache"

        indexes = [
            models.Index(
                fields=["city", "state", "country"],
                name="weathercache_index",
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["city", "state", "country"],
                name="unique_weather_cache_location",
            )
        ]

    @property
    def is_valid(self) -> bool:
        """
        Determines whether this cache entry is still valid.
        """
        return self.updated_at >= timezone.now() - get_weather_cache_expiry_delta()

    def __str__(self) -> str:
        parts = [self.city, self.state, self.country]
        return ", ".join(part for part in parts if part)


# ============================================================
# Search History
# ============================================================


class SearchHistory(models.Model):
    """
    Tracks user search history without duplicating weather JSON.
    References WeatherCache as the single source of truth.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="search_history",
    )

    weather_cache = models.JSONField(
        help_text="Weather data payload", null=True, blank=True
    )

    city_name_queried = models.CharField(max_length=100)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

        indexes = [
            models.Index(fields=["user"], name="search_history_user_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} searched {self.city_name_queried}"
