from django.contrib import admin
from .models import GrantApplication


@admin.register(GrantApplication)
class GrantApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'full_name', 'travel_from_display', 'travel_amount', 
        'request_travel', 'request_accommodation', 'request_ticket', 'created_at'
    ]
    list_filter = [
        'gender', 'transportation_type', 
        'request_travel', 'request_accommodation', 'request_ticket',
        'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'travel_from_city', 'travel_from_country'
    ]
    readonly_fields = [
        'user', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Application Info', {
            'fields': ('user', 'created_at', 'updated_at')
        }),
        ('Personal Information', {
            'fields': ('gender', 'gender_details', 'current_role', 'current_role_details')
        }),
        ('Application Details', {
            'fields': ('motivation', 'contribution', 'financial_need')
        }),
        ('Travel Information', {
            'fields': ('request_travel', 'travel_from_city', 'travel_from_country', 'travel_amount', 'transportation_type')
        }),
        ('Accommodation & Ticket', {
            'fields': ('request_accommodation', 'accommodation_nights', 'request_ticket')
        }),
        ('Additional Information', {
            'fields': ('additional_info',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    full_name.short_description = 'Full Name'
    
    def travel_from_display(self, obj):
        return obj.travel_from or "Not specified"
    travel_from_display.short_description = 'Travel From'
    