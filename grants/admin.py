from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
from .models import GrantApplication, GrantReview
from .utils import export_applications_to_excel

class GrantReviewInline(admin.TabularInline):
    model = GrantReview
    extra = 0
    readonly_fields = ('reviewer', 'score', 'notes', 'suggested_amount', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(GrantApplication)
class GrantApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'full_name', 'status', 'travel_from', 'travel_amount', 
        'average_score', 'amount_granted', 'decision_maker', 'created_at'
    ]
    list_filter = [
        'status', 'gender', 'talk_proposal', 'transportation_type', 
        'decision_maker', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'travel_from_city', 'travel_from_country'
    ]
    readonly_fields = [
        'user', 'created_at', 'updated_at', 'average_score', 
        'suggested_amount_average', 'review_count'
    ]
    
    inlines = [GrantReviewInline]
    
    fieldsets = (
        ('Application Info', {
            'fields': ('user', 'status', 'created_at', 'updated_at')
        }),
        ('Personal Information', {
            'fields': ('gender', 'talk_proposal', 'additional_info')
        }),
        ('Travel Information', {
            'fields': ('travel_from_city', 'travel_from_country', 'travel_amount', 'transportation_type')
        }),
        ('Review Summary', {
            'fields': ('review_count', 'average_score', 'suggested_amount_average'),
            'classes': ('collapse',)
        }),
        ('Decision', {
            'fields': ('decision_maker', 'amount_granted', 'decision_notes'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_to_excel', 'mark_as_approved', 'mark_as_rejected']
    
    def export_to_excel(self, request, queryset):
        """Export selected applications to Excel"""
        return export_applications_to_excel(queryset, 'selected_applications')
    export_to_excel.short_description = "Export selected applications to Excel"
    
    def mark_as_approved(self, request, queryset):
        """Mark selected applications as approved"""
        if not request.user.has_perm('grants.can_make_grant_decisions'):
            self.message_user(request, "You don't have permission to make grant decisions.", level='ERROR')
            return
        
        updated = queryset.update(status='approved', decision_maker=request.user)
        self.message_user(request, f'{updated} applications marked as approved.')
    mark_as_approved.short_description = "Mark selected applications as approved"
    
    def mark_as_rejected(self, request, queryset):
        """Mark selected applications as rejected"""
        if not request.user.has_perm('grants.can_make_grant_decisions'):
            self.message_user(request, "You don't have permission to make grant decisions.", level='ERROR')
            return
        
        updated = queryset.update(status='rejected', decision_maker=request.user)
        self.message_user(request, f'{updated} applications marked as rejected.')
    mark_as_rejected.short_description = "Mark selected applications as rejected"
    
    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    full_name.short_description = 'Full Name'
    
    def review_count(self, obj):
        return obj.reviews.count()
    review_count.short_description = 'Reviews'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('reviews', 'user')
    
    def has_change_permission(self, request, obj=None):
        # Allow reviewers to view but restrict editing based on permissions
        if obj and not request.user.has_perm('grants.can_make_grant_decisions'):
            # Reviewers can only view, not edit the main application
            return False
        return super().has_change_permission(request, obj)

@admin.register(GrantReview)
class GrantReviewAdmin(admin.ModelAdmin):
    list_display = ['application', 'reviewer', 'score', 'suggested_amount', 'created_at']
    list_filter = ['score', 'created_at', 'reviewer']
    search_fields = [
        'application__user__username', 'application__user__email',
        'reviewer__username', 'reviewer__email', 'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Info', {
            'fields': ('application', 'reviewer', 'created_at', 'updated_at')
        }),
        ('Review Details', {
            'fields': ('score', 'suggested_amount', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Reviewers can only see their own reviews unless they're decision makers
        if not request.user.has_perm('grants.can_make_grant_decisions'):
            queryset = queryset.filter(reviewer=request.user)
        return queryset.select_related('application__user', 'reviewer')
    
    def has_change_permission(self, request, obj=None):
        # Reviewers can only edit their own reviews
        if obj and not request.user.has_perm('grants.can_make_grant_decisions'):
            return obj.reviewer == request.user
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # Only decision makers can delete reviews
        return request.user.has_perm('grants.can_make_grant_decisions')

# Register permissions for easy assignment
admin.site.register(Permission)
