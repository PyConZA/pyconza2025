from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import GrantApplication

class GrantApplicationForm(forms.ModelForm):
    class Meta:
        model = GrantApplication
        fields = [
            'phone_number',
            'motivation',
            'contribution',
            'financial_need',
            'talk_proposal',
            'talk_proposal_details',
            'gender',
            'gender_details',
            'current_role',
            'current_role_details',
            'transportation_type',
            'request_travel',
            'travel_amount',
            'travel_from',
            'request_accommodation',
            'accommodation_nights',
            'request_ticket',
            'conference_benefit',
            'additional_info',
        ]
        
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'motivation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us why you want to attend PyCon Africa...'
            }),
            'contribution': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your contributions to the Python community...'
            }),
            'financial_need': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain your financial circumstances...'
            }),
            'talk_proposal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'talk_proposal_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Please provide more details...'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'gender_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Please provide more details...'
            }),
            'current_role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'current_role_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Please provide more details...'
            }),
            'transportation_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'travel_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'travel_from': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'accommodation_nights': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'conference_benefit': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'How will attending PyCon Africa benefit you personally and professionally?'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional information you would like to share...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make certain fields required
        self.fields['phone_number'].required = True
        self.fields['talk_proposal'].required = True
        self.fields['gender'].required = True
        self.fields['current_role'].required = True
        self.fields['conference_benefit'].required = True
        
        # Set up conditional fields
        self.fields['talk_proposal_details'].required = False
        self.fields['gender_details'].required = False
        self.fields['current_role_details'].required = False
        self.fields['additional_info'].required = False

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate conditional fields
        talk_proposal = cleaned_data.get('talk_proposal')
        if talk_proposal == 'other' and not cleaned_data.get('talk_proposal_details'):
            self.add_error('talk_proposal_details', 'Please provide details when selecting "Other".')
        
        gender = cleaned_data.get('gender')
        if gender == 'other' and not cleaned_data.get('gender_details'):
            self.add_error('gender_details', 'Please provide details when selecting "Other".')
        
        current_role = cleaned_data.get('current_role')
        if current_role == 'other' and not cleaned_data.get('current_role_details'):
            self.add_error('current_role_details', 'Please provide details when selecting "Other".')
        
        # Validate travel-related fields
        request_travel = cleaned_data.get('request_travel')
        if request_travel:
            if not cleaned_data.get('travel_amount'):
                self.add_error('travel_amount', 'Please specify the travel amount.')
            if not cleaned_data.get('travel_from'):
                self.add_error('travel_from', 'Please specify where you will be traveling from.')
            if not cleaned_data.get('transportation_type'):
                self.add_error('transportation_type', 'Please specify your transportation type.')
        
        # Validate accommodation-related fields
        request_accommodation = cleaned_data.get('request_accommodation')
        if request_accommodation and not cleaned_data.get('accommodation_nights'):
            self.add_error('accommodation_nights', 'Please specify the number of nights.')
        
        return cleaned_data

class GrantReviewForm(forms.ModelForm):
    class Meta:
        model = GrantApplication
        fields = ['status', 'reviewer_notes', 'amount_granted']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reviewer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add your review notes here...'
            }),
            'amount_granted': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }

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