from django.urls import path
from .views import WeatherView, SearchHistoryListView

urlpatterns = [

    path('weather/', WeatherView.as_view(), name='weather'),
    path('history/', SearchHistoryListView.as_view(), name='search_history'),
]


