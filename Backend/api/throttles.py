
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class WeatherAnonThrottle(AnonRateThrottle):
    scope = 'weather_limited'

class WeatherUserThrottle(UserRateThrottle):
    scope = 'weather_burst'
