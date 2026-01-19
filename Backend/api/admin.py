from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, WeatherCache, SearchHistory

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin): # Use UserAdmin for better layout of custom user models
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
    # Add phone to the fieldsets so it shows up in the edit page
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone',)}),
    )

@admin.register(WeatherCache)
class WeatherCacheAdmin(admin.ModelAdmin):
    list_display = ('city', 'country', 'updated_at', 'is_valid_status')
    search_fields = ('city', 'country')
    readonly_fields = ('updated_at',)

    # We rename the method to avoid conflict with the @property 'is_valid'
    def is_valid_status(self, obj):
        return obj.is_valid
    is_valid_status.boolean = True # Shows a nice Green Check / Red X icon
    is_valid_status.short_description = "Fresh Data"

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    # 'city_name_queried' is the field name in our optimized model
    list_display = ('user', 'city_name_queried', 'timestamp', 'get_status')
    search_fields = ('user__username', 'city_name_queried')
    list_filter = ('timestamp',)

    def get_status(self, obj):
        # Accessing the code through the related cache_item
        if obj.cache_item and obj.cache_item.data:
            return obj.cache_item.data.get('cod', '200')
        return 'N/A'
    get_status.short_description = "API Status"