from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries import countries
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django_select2.forms import Select2Widget
from .models import GrantApplication
import re


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
            'additional_info',
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+27123456789 (include country code)',
                'pattern': r'^\+?[1-9]\d{1,14}$',
                'title': 'Enter phone number with country code (e.g., +27123456789)'
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

    def clean_phone_number(self):
        """Clean and validate phone number"""
        phone = self.cleaned_data.get('phone_number', '').strip()
        
        if not phone:
            raise forms.ValidationError(_("Phone number is required."))
        
        # Remove common formatting characters
        phone_cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone)
        
        # Ensure it starts with + if it doesn't already
        if not phone_cleaned.startswith('+'):
            # If it starts with 00, replace with +
            if phone_cleaned.startswith('00'):
                phone_cleaned = '+' + phone_cleaned[2:]
            # If it looks like a local number, suggest adding country code
            elif phone_cleaned.isdigit() and len(phone_cleaned) >= 9:
                raise forms.ValidationError(_(
                    "Please include your country code. For example: +27 for South Africa, +1 for USA/Canada, +44 for UK."
                ))
            else:
                phone_cleaned = '+' + phone_cleaned
        
        # Validate format: + followed by 1-3 digit country code, then 6-12 digits
        if not re.match(r'^\+[1-9]\d{8,14}$', phone_cleaned):
            raise forms.ValidationError(_(
                "Please enter a valid phone number with country code. "
                "Format: +[country code][phone number] (e.g., +27123456789)"
            ))
        
        # Check length (E.164 standard allows max 15 digits including country code)
        if len(phone_cleaned) > 15:
            raise forms.ValidationError(_(
                "Phone number is too long. Maximum 15 digits including country code."
            ))
        
        if len(phone_cleaned) < 10:
            raise forms.ValidationError(_(
                "Phone number is too short. Please include country code and full number."
            ))
        
        return phone_cleaned

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
