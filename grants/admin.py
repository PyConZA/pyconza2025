from django.contrib import admin
from django.utils.html import format_html
from .models import GrantApplication

@admin.register(GrantApplication)
class GrantApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at', 'reviewed_at', 'amount_granted', 'get_requests']
    list_filter = ['status', 'request_travel', 'request_accommodation', 'request_ticket', 'created_at']
    search_fields = ['user__username', 'user__email', 'travel_from']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
    
    fieldsets = (
        ('Applicant Information', {
            'fields': ('user', 'created_at', 'updated_at')
        }),
        ('Application Details', {
            'fields': ('motivation', 'contribution', 'financial_need')
        }),
        ('Requests', {
            'fields': (
                'request_travel', 'travel_amount', 'travel_from',
                'request_accommodation', 'accommodation_nights',
                'request_ticket'
            )
        }),
        ('Review', {
            'fields': ('status', 'reviewer_notes', 'amount_granted', 'reviewed_at')
        }),
    )

    def get_requests(self, obj):
        requests = []
        if obj.request_travel:
            requests.append(f'Travel (R{obj.travel_amount})')
        if obj.request_accommodation:
            requests.append(f'Accommodation ({obj.accommodation_nights} nights)')
        if obj.request_ticket:
            requests.append('Ticket')
        return format_html('<br>'.join(requests))
    get_requests.short_description = 'Requests'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.status not in ['submitted', 'under_review']:
            readonly_fields.extend([
                'motivation', 'contribution', 'financial_need',
                'request_travel', 'travel_amount', 'travel_from',
                'request_accommodation', 'accommodation_nights',
                'request_ticket'
            ])
        return readonly_fields
