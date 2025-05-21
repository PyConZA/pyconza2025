from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.utils import timezone

from .models import GrantApplication
from .forms import GrantApplicationForm, GrantReviewForm

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
        # Allow editing if application is in submitted state
        if obj.status == 'submitted':
            return obj.user == self.request.user
        # Allow accepting/declining if application is approved
        elif obj.status == 'approved':
            return obj.user == self.request.user
        return False

    def get_object(self, queryset=None):
        return self.request.user.grant_application

    def post(self, request, *args, **kwargs):
        # Handle accept/decline actions
        if 'status' in request.POST and self.get_object().status == 'approved':
            new_status = request.POST.get('status')
            if new_status in ['accepted', 'declined']:
                application = self.get_object()
                application.status = new_status
                application.save()
                messages.success(
                    request,
                    'Grant successfully accepted. We will be in touch soon!' if new_status == 'accepted'
                    else 'Grant has been declined. Thank you for letting us know.'
                )
                return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Your grant application has been updated successfully!')
        return super().form_valid(form)

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
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        return context

class GrantApplicationReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = GrantApplication
    form_class = GrantReviewForm
    template_name = 'grants/application_review.html'
    success_url = reverse_lazy('grants:application_list')

    def test_func(self):
        return self.request.user.has_perm('grants.can_review_grants')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Grant application review has been saved.')
        return response
