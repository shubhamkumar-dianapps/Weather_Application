from rest_framework import serializers

from .models import WeatherCache, SearchHistory


# ============================================================
# Weather Cache Serializer
# ============================================================


class WeatherCacheSerializer(serializers.ModelSerializer):
    """
    Serializer for WeatherCache.

    Uses JSONField intentionally because the weather provider
    response schema may change over time.
    """

    is_valid = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WeatherCache
        fields = (
            "id",
            "city",
            "state",
            "country",
            "data",
            "updated_at",
            "is_valid",
        )
        read_only_fields = ("updated_at",)

    # ------------------------
    # Computed fields
    # ------------------------

    def get_is_valid(self, obj) -> bool:
        return obj.is_valid

    # ------------------------
    # Field-level validations
    # ------------------------

    def validate_city(self, value: str) -> str:
        """
        Normalize city name to avoid cache duplication.
        """
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("City name cannot be empty.")
        return cleaned.title()

    def validate_state(self, value: str | None) -> str | None:
        """
        Normalize state name (optional field).
        """
        return value.strip().title() if value else value

    def validate_country(self, value: str) -> str:
        """
        Normalize country code/name.
        """
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise serializers.ValidationError(
                "Country must be at least 2 characters long."
            )
        return cleaned.upper()

    def validate_data(self, value: dict) -> dict:
        """
        Ensure weather payload is not empty.
        """
        if not value:
            raise serializers.ValidationError("Weather data payload cannot be empty.")
        return value


# ============================================================
# Search History Serializer
# ============================================================


class SearchHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for SearchHistory.
    """

    city = serializers.CharField(source="weather_cache.city", read_only=True)

    country = serializers.CharField(source="weather_cache.country", read_only=True)

    class Meta:
        model = SearchHistory
        fields = (
            "id",
            "city_name_queried",
            "city",
            "country",
            "weather_cache",
            "timestamp",
        )
        read_only_fields = ("timestamp", "weather_cache")

    # ------------------------
    # Object-level validation
    # ------------------------

    def validate_city_name_queried(self, value: str) -> str:
        """
        Normalize searched city name.
        """
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("City name cannot be empty.")
        return cleaned.title()
