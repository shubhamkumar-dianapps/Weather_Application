from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, WeatherCache, SearchHistory

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone',)}),
    )

@admin.register(WeatherCache)
class WeatherCacheAdmin(admin.ModelAdmin):
    list_display = ('city', 'country', 'updated_at', 'is_valid_status')
    search_fields = ('city', 'country')
    readonly_fields = ('updated_at',)

    def is_valid_status(self, obj):
        return obj.is_valid
    is_valid_status.boolean = True
    is_valid_status.short_description = "Fresh Data"

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'city_name_queried', 'timestamp', 'get_status')
    search_fields = ('user__username', 'city_name_queried')
    list_filter = ('timestamp',)

    def get_status(self, obj):
        if obj.response_data:
            return obj.response_data.get('cod', '200')
        return 'N/A'
    get_status.short_description = "API Status"
