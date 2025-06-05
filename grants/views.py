from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.views import View
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import GrantApplication
from .forms import GrantApplicationForm

# Create your views here.

class GrantApplicationCreateView(LoginRequiredMixin, CreateView):
    model = GrantApplication
    form_class = GrantApplicationForm
    template_name = 'grants/application_form.html'

    def get_success_url(self):
        return reverse('grants:application_detail')

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

    def get_success_url(self):
        return reverse('grants:application_detail')

    def test_func(self):
        try:
            obj = self.request.user.grant_application
            # Only allow editing if application is in submitted state
            # Once it moves to any other state, no editing allowed
            return obj.status == 'submitted' and obj.user == self.request.user
        except GrantApplication.DoesNotExist:
            return False

    def get_object(self, queryset=None):
        return self.request.user.grant_application

    def form_valid(self, form):
        messages.success(self.request, 'Your grant application has been updated successfully!')
        return super().form_valid(form)

class GrantApplicationDetailView(LoginRequiredMixin, DetailView):
    model = GrantApplication
    template_name = 'grants/application_detail.html'
    context_object_name = 'application'

    def get_object(self, queryset=None):
        try:
            return self.request.user.grant_application
        except GrantApplication.DoesNotExist:
            messages.error(self.request, 'You have not submitted a grant application yet.')
            return redirect('grants:application_create')

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        except:
            messages.error(request, 'You have not submitted a grant application yet.')
            return redirect('grants:application_create')

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
        
        if status:
            queryset = queryset.filter(status=status)
        if gender:
            queryset = queryset.filter(gender=gender)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['gender_filter'] = self.request.GET.get('gender', '')
        
        return context
