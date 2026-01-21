from rest_framework.pagination import CursorPagination


class WeatherHistoryPagination(CursorPagination):
    page_size = 5
    ordering = "-timestamp"
    cursor_query_param = "cursor"
