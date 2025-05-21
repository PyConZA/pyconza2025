from django import forms
from django.utils import timezone
from .models import GrantApplication

class GrantApplicationForm(forms.ModelForm):
    class Meta:
        model = GrantApplication
        fields = [
            'motivation',
            'contribution',
            'financial_need',
            'request_travel',
            'travel_amount',
            'travel_from',
            'request_accommodation',
            'accommodation_nights',
            'request_ticket',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required only if their corresponding request is True
        self.fields['travel_amount'].required = False
        self.fields['travel_from'].required = False
        self.fields['accommodation_nights'].required = False

    def clean(self):
        cleaned_data = super().clean()
        request_travel = cleaned_data.get('request_travel')
        travel_amount = cleaned_data.get('travel_amount')
        travel_from = cleaned_data.get('travel_from')
        request_accommodation = cleaned_data.get('request_accommodation')
        accommodation_nights = cleaned_data.get('accommodation_nights')

        if request_travel and not travel_amount:
            self.add_error('travel_amount', 'Please provide estimated travel costs')
        if request_travel and not travel_from:
            self.add_error('travel_from', 'Please specify where you will travel from')
        if request_accommodation and not accommodation_nights:
            self.add_error('accommodation_nights', 'Please specify number of nights needed')

        return cleaned_data

class GrantReviewForm(forms.ModelForm):
    class Meta:
        model = GrantApplication
        fields = ['status', 'reviewer_notes', 'amount_granted']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit status choices for reviewers
        self.fields['status'].choices = [
            choice for choice in self.fields['status'].choices
            if choice[0] in ['under_review', 'approved', 'rejected']
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.status in ['approved', 'rejected']:
            instance.reviewed_at = timezone.now()
        if commit:
            instance.save()
        return instance 