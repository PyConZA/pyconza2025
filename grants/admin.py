from django.contrib import admin
from django.utils.html import format_html
from .models import GrantApplication

@admin.register(GrantApplication)
class GrantApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'gender', 'current_role', 'talk_proposal', 'created_at', 'reviewed_at', 'amount_granted', 'get_requests']
    list_filter = [
        'status', 'gender', 'current_role', 'talk_proposal', 'transportation_type',
        'request_travel', 'request_accommodation', 'request_ticket', 'created_at'
    ]
    search_fields = ['user__username', 'user__email', 'travel_from', 'phone_number']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
    
    fieldsets = (
        ('Applicant Information', {
            'fields': ('user', 'phone_number', 'created_at', 'updated_at')
        }),
        ('Demographics', {
            'fields': (
                'gender', 'gender_details',
                'current_role', 'current_role_details'
            )
        }),
        ('Talk Proposal', {
            'fields': ('talk_proposal', 'talk_proposal_details')
        }),
        ('Application Details', {
            'fields': ('motivation', 'contribution', 'financial_need')
        }),
        ('Travel & Transportation', {
            'fields': (
                'request_travel', 'travel_amount', 'travel_from', 'transportation_type'
            )
        }),
        ('Accommodation & Tickets', {
            'fields': (
                'request_accommodation', 'accommodation_nights',
                'request_ticket'
            )
        }),
        ('Additional Information', {
            'fields': ('conference_benefit', 'additional_info')
        }),
        ('Review', {
            'fields': ('status', 'reviewer_notes', 'amount_granted', 'reviewed_at')
        }),
    )

    def get_requests(self, obj):
        requests = []
        if obj.request_travel:
            requests.append(f'Travel (${obj.travel_amount})')
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
                'phone_number', 'gender', 'gender_details', 'current_role', 'current_role_details',
                'talk_proposal', 'talk_proposal_details', 'transportation_type',
                'motivation', 'contribution', 'financial_need', 'conference_benefit', 'additional_info',
                'request_travel', 'travel_amount', 'travel_from',
                'request_accommodation', 'accommodation_nights',
                'request_ticket'
            ])
        return readonly_fields
