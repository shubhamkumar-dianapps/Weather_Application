from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SearchHistory
import requests

from .services import WeatherService
from .throttles import WeatherAnonThrottle, WeatherUserThrottle

from .serializers import SearchHistorySerializer





class WeatherView(APIView):
    """

    API view to get weather data. 
    Checks local cache first, creating a mock response if not found (placeholder for external API).
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [WeatherAnonThrottle, WeatherUserThrottle]


    def get(self, request):
        city = request.query_params.get('city')
        state = request.query_params.get('state')
        country = request.query_params.get('country')

        if not city:
            return Response({"error": "City parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not state:
            return Response({"error": "State parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not country:
            return Response({"error": "Country parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        # Use Service Layer
        try:
            data = WeatherService.fetch_weather(city, state, country)
            
        except requests.exceptions.RequestException as e:
            # Handle potential external API errors gracefully
            error_details = {"error": "Failed to fetch weather data from upstream provider."}
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

            if e.response is not None:
                status_code = e.response.status_code
                try:
                    error_details["upstream_error"] = e.response.json()
                except ValueError:
                     error_details["upstream_error"] = e.response.text
            
            return Response(error_details, status=status_code)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Log Search History (if authenticated)
        if request.user.is_authenticated:
            WeatherService.log_history(request.user, city, data)

        return Response(data, status=status.HTTP_200_OK)

class SearchHistoryListView(generics.ListAPIView):
    """
    API view to list search history for the authenticated user.
    """
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optimize query to fetch related user data in a single query (solves potential N+1)
        return SearchHistory.objects.filter(user=self.request.user).select_related('user')



