import logging
import requests

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SearchHistory
from .serializers import SearchHistorySerializer
from .services import WeatherService
from .throttles import WeatherAnonThrottle, WeatherUserThrottle
from core.pagination import WeatherHistoryPagination

logger = logging.getLogger(__name__)


class WeatherView(APIView):
    """
    Retrieve weather information for a given location.
    Uses cache-first strategy with external API fallback.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [WeatherAnonThrottle, WeatherUserThrottle]

    def get(self, request):
        city = request.query_params.get("city")
        state = request.query_params.get("state")
        country = request.query_params.get("country")

        # Validate required parameters
        missing_params = [
            param
            for param, value in {
                "city": city,
                "state": state,
                "country": country,
            }.items()
            if not value
        ]

        if missing_params:
            return Response(
                {"error": f"Missing required parameters: {', '.join(missing_params)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = WeatherService.fetch_weather(city, state, country)

        except requests.exceptions.Timeout:
            logger.warning("Weather API timeout")
            return Response(
                {"error": "Weather service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except requests.exceptions.RequestException:
            logger.error("Upstream weather API failure", exc_info=True)
            return Response(
                {"error": "Failed to fetch weather data."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception:
            logger.exception("Unexpected error in WeatherView")
            return Response(
                {"error": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Log search history (non-blocking)
        if request.user.is_authenticated:
            try:
                WeatherService.log_history(request.user, city, data)
            except Exception:
                logger.warning("Failed to log search history", exc_info=True)

        return Response(data, status=status.HTTP_200_OK)


class SearchHistoryListView(generics.ListAPIView):
    """
    List weather search history for the authenticated user.
    """

    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = WeatherHistoryPagination

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user).select_related(
            "user"
        )
