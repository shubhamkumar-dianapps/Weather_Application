from rest_framework import serializers
from .models import WeatherCache, SearchHistory



# UserSerializer moved to 'authorization' app

class WeatherCacheSerializer(serializers.ModelSerializer):

    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = WeatherCache
        fields = ['id', 'city', 'state', 'country', 'data', 'updated_at', 'is_valid']
        read_only_fields = ['updated_at']

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'user', 'city_name_queried', 'response_data', 'timestamp']
        read_only_fields = ['timestamp', 'user']
