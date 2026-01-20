import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.services import WeatherService





cities = [
    ("Patna", "Bihar", "IN"),
    ("Delhi", "Delhi", "IN"),
    ("Kolkata", "West Bengal", "IN")
]

print("--- Starting Weather Service Test ---")
for city, state, country in cities:
    try:
        print(f"\nFetching for {city}, {state}, {country}...")
        data = WeatherService.fetch_weather(city, state, country)
        
        # Extract some readable info for verify
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        
        print("[OK] Success!")
        print(f"   Temp: {main.get('temp')} C")
        print(f"   Condition: {weather.get('description')}")
        print(f"   Coordinates: {data.get('coord')}")
        
    except Exception as e:
        print(f"[FAIL] Failed: {e}")


print("\n--- Test Complete ---")
