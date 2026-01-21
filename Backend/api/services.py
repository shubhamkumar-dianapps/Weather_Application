import logging
from typing import Optional, Dict, Any

import requests
import os
from .models import WeatherCache, SearchHistory

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service layer responsible for:
    - Weather cache lookup
    - External API communication
    - Cache persistence
    - Search history logging
    """

    API_KEY: str = os.getenv("WEATHER_API_KEY")
    BASE_URL: str = os.getenv("BASE_URL")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT_FOR_SERVICE"))  # seconds

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    @classmethod
    def fetch_weather(
        cls, city: str, state: Optional[str] = None, country: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch weather data using cache-first strategy.
        """

        normalized_city = cls._normalize(city)
        normalized_state = cls._normalize(state)
        normalized_country = cls._normalize(country)

        # Cache lookup
        cached = WeatherCache.objects.get_valid_cache(
            normalized_city,
            normalized_state,
            normalized_country,
        )
        if cached:
            logger.info("Weather fetched from cache: %s", normalized_city)
            return cached.data

        # External API call
        api_data = cls._fetch_from_provider(
            normalized_city,
            normalized_state,
            normalized_country,
        )

        # Persist cache
        weather_cache = cls._save_cache(
            api_data,
            normalized_state,
        )

        return weather_cache.data

    @staticmethod
    def log_history(user, city_queried: str, data: Dict[str, Any]) -> None:
        """
        Persist user search history (only for authenticated users).
        """
        if not user or not user.is_authenticated:
            return
        # As of now I am updating the search history with the response data in future I add count variable if user refresh or search same city multiple times
        SearchHistory.objects.update_or_create(
            user=user,
            city_name_queried=city_queried.strip(),
            defaults={
                "weather_cache": data,
            },
        )

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    @staticmethod
    def _normalize(value: Optional[str]) -> Optional[str]:
        """
        Normalize user input safely.
        """
        return value.strip().upper() if value else None

    @classmethod
    def _fetch_from_provider(
        cls,
        city: str,
        state: Optional[str],
        country: Optional[str],
    ) -> Dict[str, Any]:
        """
        Call third-party weather API.
        """
        query_parts = [city]
        if state:
            query_parts.append(state)
        if country:
            query_parts.append(country)

        params = {
            "q": ",".join(query_parts),
            "appid": cls.API_KEY,
            "units": "metric",
        }

        try:
            logger.info("Calling weather API for %s", city)
            response = requests.get(
                cls.BASE_URL,
                params=params,
                timeout=cls.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as exc:
            logger.error("Weather API failed: %s", exc, exc_info=True)
            raise RuntimeError("Failed to fetch weather data") from exc

    @staticmethod
    def _save_cache(
        api_data: Dict[str, Any],
        state: Optional[str],
    ) -> WeatherCache:
        """
        Persist or update weather cache entry using canonical API values.
        """

        canonical_city = api_data.get("name", "").upper()
        canonical_country = api_data.get("sys", {}).get("country", "").upper()

        weather_cache, _ = WeatherCache.objects.update_or_create(
            city=canonical_city,
            state=state,
            country=canonical_country,
            defaults={
                "data": api_data,
            },
        )

        return weather_cache
