from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries import countries
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django_select2.forms import Select2Widget
from .models import GrantApplication, GrantReview


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
            'travel_from_city',
            'travel_from_country',
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
                'rows': 5,
                'placeholder': 'Tell us why you want to attend PyCon Africa...'
            }),
            'contribution': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your contributions to the Python community...'
            }),
            'financial_need': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain your financial circumstances...'
            }),
            'talk_proposal': forms.Select(attrs={'class': 'form-select'}),
            'talk_proposal_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please provide more details...'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'gender_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Please specify...'
            }),
            'current_role': forms.Select(attrs={'class': 'form-select'}),
            'current_role_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Please specify...'
            }),
            'transportation_type': forms.Select(attrs={'class': 'form-select'}),
            'request_travel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'travel_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'travel_from_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Lagos, Cape Town, Nairobi'
            }),
            'travel_from_country': CountrySelectWidget(attrs={'class': 'form-select'}),
            'request_accommodation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'accommodation_nights': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Number of nights'
            }),
            'request_ticket': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'conference_benefit': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'How will attending benefit you?'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional information...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set help text for travel fields
        self.fields['travel_from_city'].help_text = _("Enter the city you'll be traveling from")
        self.fields['travel_from_country'].help_text = _("Select the country you'll be traveling from")
        
        # Make certain fields required
        self.fields['phone_number'].required = True
        self.fields['motivation'].required = True
        self.fields['contribution'].required = True
        self.fields['financial_need'].required = True

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate travel fields
        request_travel = cleaned_data.get('request_travel')
        travel_amount = cleaned_data.get('travel_amount')
        travel_from_city = cleaned_data.get('travel_from_city')
        travel_from_country = cleaned_data.get('travel_from_country')
        transportation_type = cleaned_data.get('transportation_type')
        
        if request_travel:
            if not travel_amount:
                raise forms.ValidationError(_("Travel amount is required when requesting travel assistance."))
            if not travel_from_city:
                raise forms.ValidationError(_("Travel from city is required when requesting travel assistance."))
            if not travel_from_country:
                raise forms.ValidationError(_("Travel from country is required when requesting travel assistance."))
            if not transportation_type:
                raise forms.ValidationError(_("Transportation type is required when requesting travel assistance."))
        
        # Validate accommodation fields
        request_accommodation = cleaned_data.get('request_accommodation')
        accommodation_nights = cleaned_data.get('accommodation_nights')
        
        if request_accommodation and not accommodation_nights:
            raise forms.ValidationError(_("Number of accommodation nights is required when requesting accommodation assistance."))
        
        # Validate conditional detail fields
        gender = cleaned_data.get('gender')
        gender_details = cleaned_data.get('gender_details')
        
        if gender == 'other' and not gender_details:
            raise forms.ValidationError(_("Please provide gender details when selecting 'Other'."))
        
        current_role = cleaned_data.get('current_role')
        current_role_details = cleaned_data.get('current_role_details')
        
        if current_role == 'other' and not current_role_details:
            raise forms.ValidationError(_("Please provide role details when selecting 'Other'."))
        
        talk_proposal = cleaned_data.get('talk_proposal')
        talk_proposal_details = cleaned_data.get('talk_proposal_details')
        
        if talk_proposal == 'other' and not talk_proposal_details:
            raise forms.ValidationError(_("Please provide talk proposal details when selecting 'Other'."))
        
        return cleaned_data


class GrantReviewForm(forms.ModelForm):
    """Form for reviewers to score and provide feedback"""
    class Meta:
        model = GrantReview
        fields = ['score', 'notes', 'suggested_amount']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'placeholder': 'Score 1-10'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add your review notes and feedback here...'
            }),
            'suggested_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Suggested amount in USD'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].help_text = _("Rate this application from 1 (lowest) to 10 (highest)")
        self.fields['notes'].help_text = _("Provide detailed feedback about this application")
        self.fields['suggested_amount'].help_text = _("Suggest the amount to grant (optional)")


class GrantDecisionForm(forms.ModelForm):
    """Form for decision makers to make final approve/reject decisions"""
    class Meta:
        model = GrantApplication
        fields = ['status', 'amount_granted', 'decision_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'amount_granted': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Final amount to grant'
            }),
            'decision_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Final decision notes...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit status choices for decision makers
        self.fields['status'].choices = [
            choice for choice in self.fields['status'].choices
            if choice[0] in ['under_review', 'approved', 'rejected']
        ]
        
        self.fields['amount_granted'].help_text = _("Final amount to grant in USD")
        self.fields['decision_notes'].help_text = _("Notes about the final decision")

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.status in ['approved', 'rejected']:
            instance.reviewed_at = timezone.now()
        if commit:
            instance.save()
        return instance 