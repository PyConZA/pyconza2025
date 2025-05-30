from django.urls import path
from . import views

app_name = 'grants'

urlpatterns = [
    path('', views.GrantApplicationCreateView.as_view(), name='application_create'),
    path('application/', views.GrantApplicationDetailView.as_view(), name='application_detail'),
    path('application/edit/', views.GrantApplicationUpdateView.as_view(), name='application_update'),
    path('application/respond/', views.GrantApplicationResponseView.as_view(), name='application_respond'),
    path('applications/', views.GrantApplicationListView.as_view(), name='application_list'),
    path('applications/export/', views.GrantApplicationExportView.as_view(), name='application_export'),
    path('applications/<int:pk>/review/', views.GrantApplicationReviewView.as_view(), name='application_review'),
    path('applications/<int:pk>/decision/', views.GrantApplicationDecisionView.as_view(), name='application_decision'),
] 