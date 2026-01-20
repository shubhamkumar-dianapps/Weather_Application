import requests
from django.conf import settings
from django.utils import timezone
from .models import WeatherCache, SearchHistory

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
            SearchHistory.objects.update_or_create(
                user=user,
                city_name_queried=city,
                defaults={
                    'response_data': data
                }
            )

    @classmethod
    def fetch_weather(cls, city, state=None, country=None):
        """
        Full logic: Cache Check -> External API Fetch -> Cache Save
        """
        # 1. Try to get valid data from our optimized Database Manager
        cached_entry = WeatherCache.objects.get_valid_cache(city, state, country)
        if cached_entry:
            print(f"Data fetched from DB for {city}")
            return cached_entry.data  # Return just the data dict

        # 2. If no valid cache, call OpenWeatherMap
        # Construct query: city,state,country code or just city,country
        # OWM uses ISO 3166 country codes. If 'country' is a full name, it might fail or fuzzy match.
        # Ideally, we pass what we have.
        query_parts = [city]
        if state:
            query_parts.append(state)
        if country:
            query_parts.append(country)
        
        q_param = ",".join(query_parts)

        params = {
            'q': q_param,
            'appid': cls.API_KEY,
            'units': 'metric'
        }

        try:
            print("API is hit")
            response = requests.get(cls.BASE_URL, params=params)
            response.raise_for_status() # Raise error for 4xx or 5xx status
            api_data = response.json()

            # 3. Update or Create Cache entry
            weather_obj, created = WeatherCache.objects.update_or_create(
                city=city,
                state=state,
                country=country if country else api_data.get('sys', {}).get('country', 'Unknown'),
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
