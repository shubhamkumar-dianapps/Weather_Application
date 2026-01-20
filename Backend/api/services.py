import requests
import logging
from django.conf import settings
from django.utils import timezone
from .models import WeatherCache, SearchHistory

logger = logging.getLogger(__name__)

class WeatherService:
    # Get your API key from settings (keep it in .env)
    API_KEY = getattr(settings, 'WEATHER_API_KEY', "fc32ffca6b17e7a997a35a4a63e670b9")
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    @staticmethod
    def log_history(user, city, data):
        """
        Logs the search history for an authenticated user.
        """
        if user.is_authenticated:
            normalized_city = city.strip().upper()
            
            SearchHistory.objects.update_or_create(
                user=user,
                city_name_queried=normalized_city,
                defaults={
                    'response_data': data
                }
            )

    @classmethod
    def fetch_weather(cls, city, state=None, country=None):
        """
        Full logic: Cache Check -> External API Fetch -> Cache Save
        """
        city = city.strip().upper()
        if state:
            state = state.strip().upper()
        if country:
            country = country.strip().upper()

        # 1. Try to get valid data from our optimized Database Manager
        # Manager uses iexact, so passing Upper remains valid
        cached_entry = WeatherCache.objects.get_valid_cache(city, state, country)
        if cached_entry:
            logger.info(f"Data fetched from DB for {city}")
            return cached_entry.data  # Return just the data dict

        # 2. If no valid cache, call OpenWeatherMap
        # Construct query: city,state,country code or just city,country
        query_parts = [city]
        if state:
            query_parts.append(state)
        # Note: If user passes 'INDIA', OWM usually handles it, returning 'IN' in sys.country
        if country:
            query_parts.append(country)
        
        q_param = ",".join(query_parts)

        params = {
            'q': q_param,
            'appid': cls.API_KEY,
            'units': 'metric'
        }

        try:
            logger.info(f"API is hit for {city}")
            response = requests.get(cls.BASE_URL, params=params)
            response.raise_for_status() # Raise error for 4xx or 5xx status
            api_data = response.json()

            # 3. Update or Create Cache entry
            # KEY FIX: Use API's standardized Name and Country (e.g. "IN" instead of "INDIA")
            # to ensure the DB stores the canonical version.
            canonical_city = api_data.get('name', city).upper()
            canonical_country = api_data.get('sys', {}).get('country', country).upper()

            weather_obj, created = WeatherCache.objects.update_or_create(
                city=canonical_city,
                state=state, # API often doesn't return state clearly, use user's normalized input
                country=canonical_country,
                defaults={
                    'data': api_data,
                    'updated_at': timezone.now()
                }
            )
            return weather_obj.data

        except requests.exceptions.RequestException as e:
            # Re-raise to be handled by the view or return None/Error dict
            # user view expects to catch Exception, so raising is fine.
            raise e


