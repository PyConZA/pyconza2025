from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
from .models import GrantApplication


@admin.register(GrantApplication)
class GrantApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'full_name', 'status', 'travel_from_display', 'travel_amount', 
        'request_travel', 'request_accommodation', 'request_ticket', 'created_at'
    ]
    list_filter = [
        'status', 'gender', 'talk_proposal', 'transportation_type', 
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
            'fields': ('user', 'status', 'created_at', 'updated_at')
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'gender', 'gender_details', 'current_role', 'current_role_details')
        }),
        ('Application Details', {
            'fields': ('motivation', 'contribution', 'financial_need')
        }),
        ('Talk Proposal', {
            'fields': ('talk_proposal', 'talk_proposal_details')
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
    
    actions = ['mark_as_approved', 'mark_as_rejected', 'mark_as_under_review']
    
    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    full_name.short_description = 'Full Name'
    
    def travel_from_display(self, obj):
        return obj.travel_from or "Not specified"
    travel_from_display.short_description = 'Travel From'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
    
    def mark_as_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} applications marked as approved.')
    mark_as_approved.short_description = 'Mark selected applications as approved'
    
    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} applications marked as rejected.')
    mark_as_rejected.short_description = 'Mark selected applications as rejected'
    
    def mark_as_under_review(self, request, queryset):
        updated = queryset.update(status='under_review')
        self.message_user(request, f'{updated} applications marked as under review.')
    mark_as_under_review.short_description = 'Mark selected applications as under review'

    def has_change_permission(self, request, obj=None):
        # Allow staff to edit applications
        return request.user.is_staff

# Register permissions for easy assignment
admin.site.register(Permission)
