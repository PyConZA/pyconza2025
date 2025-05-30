from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.views import View
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import GrantApplication, GrantReview
from .forms import GrantApplicationForm, GrantReviewForm, GrantDecisionForm
from .utils import export_applications_to_excel, get_applications_summary_stats

# Create your views here.

class GrantApplicationCreateView(LoginRequiredMixin, CreateView):
    model = GrantApplication
    form_class = GrantApplicationForm
    template_name = 'grants/application_form.html'
    success_url = reverse_lazy('grants:application_detail')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Your grant application has been submitted successfully!')
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        # Check if user already has an application
        if hasattr(request.user, 'grant_application'):
            messages.warning(request, 'You have already submitted a grant application.')
            return redirect('grants:application_detail')
        return super().get(request, *args, **kwargs)

class GrantApplicationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = GrantApplication
    form_class = GrantApplicationForm
    template_name = 'grants/application_form.html'
    success_url = reverse_lazy('grants:application_detail')

    def test_func(self):
        obj = self.get_object()
        # Only allow editing if application is in submitted state
        # Once it moves to any other state, no editing allowed
        return obj.status == 'submitted' and obj.user == self.request.user

    def get_object(self, queryset=None):
        return self.request.user.grant_application

    def form_valid(self, form):
        messages.success(self.request, 'Your grant application has been updated successfully!')
        return super().form_valid(form)

class GrantApplicationResponseView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Separate view for users to accept/decline approved grants"""
    
    def test_func(self):
        application = get_object_or_404(GrantApplication, user=self.request.user)
        return application.status == 'approved'
    
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(GrantApplication, user=request.user)
        
        # Ensure application is approved before allowing response
        if application.status != 'approved':
            messages.error(request, 'You can only respond to approved applications.')
            return redirect('grants:application_detail')
        
        new_status = request.POST.get('status')
        if new_status in ['accepted', 'declined']:
            application.status = new_status
            application.save()
            messages.success(
                request,
                'Grant successfully accepted. We will be in touch soon!' if new_status == 'accepted'
                else 'Grant has been declined. Thank you for letting us know.'
            )
        else:
            messages.error(request, 'Invalid response. Please select accept or decline.')
        
        return redirect('grants:application_detail')

class GrantApplicationDetailView(LoginRequiredMixin, DetailView):
    model = GrantApplication
    template_name = 'grants/application_detail.html'
    context_object_name = 'application'

    def get_object(self, queryset=None):
        return self.request.user.grant_application

class GrantApplicationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = GrantApplication
    template_name = 'grants/application_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def test_func(self):
        return self.request.user.has_perm('grants.can_review_grants')

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        gender = self.request.GET.get('gender')
        talk_proposal = self.request.GET.get('talk_proposal')
        
        if status:
            queryset = queryset.filter(status=status)
        if gender:
            queryset = queryset.filter(gender=gender)
        if talk_proposal:
            queryset = queryset.filter(talk_proposal=talk_proposal)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['gender_filter'] = self.request.GET.get('gender', '')
        context['talk_proposal_filter'] = self.request.GET.get('talk_proposal', '')
        
        # Add summary statistics
        context['summary_stats'] = get_applications_summary_stats(self.get_queryset())
        
        # Add user permissions for template
        context['can_make_decisions'] = self.request.user.has_perm('grants.can_make_grant_decisions')
        
        return context

class GrantApplicationExportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Export grant applications to Excel"""
    
    def test_func(self):
        return self.request.user.has_perm('grants.can_review_grants')
    
    def get(self, request, *args, **kwargs):
        # Get the same filtered queryset as the list view
        queryset = GrantApplication.objects.all()
        
        # Apply the same filters as the list view
        status = request.GET.get('status')
        gender = request.GET.get('gender')
        talk_proposal = request.GET.get('talk_proposal')
        
        if status:
            queryset = queryset.filter(status=status)
        if gender:
            queryset = queryset.filter(gender=gender)
        if talk_proposal:
            queryset = queryset.filter(talk_proposal=talk_proposal)
            
        queryset = queryset.order_by('-created_at')
        
        # Generate filename based on filters
        filename_parts = ['grant_applications']
        if status:
            filename_parts.append(f'status_{status}')
        if gender:
            filename_parts.append(f'gender_{gender}')
        if talk_proposal:
            filename_parts.append(f'talk_{talk_proposal}')
            
        filename_prefix = '_'.join(filename_parts)
        
        return export_applications_to_excel(queryset, filename_prefix)

class GrantApplicationReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for reviewers to score applications"""
    model = GrantReview
    form_class = GrantReviewForm
    template_name = 'grants/application_review.html'
    success_url = reverse_lazy('grants:application_list')

    def test_func(self):
        return self.request.user.has_perm('grants.can_review_grants')

    def get_object(self, queryset=None):
        application_pk = self.kwargs.get('pk')
        application = get_object_or_404(GrantApplication, pk=application_pk)
        
        # Get or create review for this reviewer and application
        review, created = GrantReview.objects.get_or_create(
            application=application,
            reviewer=self.request.user,
            defaults={'score': 5}  # Default score
        )
        return review

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.object.application
        context['existing_reviews'] = self.object.application.reviews.exclude(reviewer=self.request.user)
        context['can_make_decisions'] = self.request.user.has_perm('grants.can_make_grant_decisions')
        return context

    def post(self, request, *args, **kwargs):
        # Prevent editing if application has been decided
        application = self.get_object().application
        if application.status in ['approved', 'rejected']:
            messages.error(request, 'This application has already been decided. Reviews can no longer be modified.')
            return redirect('grants:application_review', pk=application.pk)
        
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Automatically change status from 'submitted' to 'under_review' when first review is saved
        application = self.object.application
        if application.status == 'submitted':
            application.status = 'under_review'
            application.save()
            messages.info(self.request, 'Application status has been updated to "Under Review".')
        
        messages.success(self.request, 'Your review has been saved successfully!')
        return response

class GrantApplicationDecisionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for decision makers to approve/reject applications"""
    model = GrantApplication
    form_class = GrantDecisionForm
    template_name = 'grants/application_decision.html'
    success_url = reverse_lazy('grants:application_list')

    def test_func(self):
        return self.request.user.has_perm('grants.can_make_grant_decisions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        context['average_score'] = self.object.average_score
        context['suggested_amount_average'] = self.object.suggested_amount_average
        return context

    def form_valid(self, form):
        # Set the decision maker
        form.instance.decision_maker = self.request.user
        response = super().form_valid(form)
        
        action = "approved" if form.instance.status == 'approved' else "rejected"
        messages.success(self.request, f'Application has been {action} successfully!')
        return response
