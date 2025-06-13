from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML, Submit
from django import forms

from website.models import VisaInvitationLetter


class VisaLetterForm(forms.ModelForm):
    class Meta:
        model = VisaInvitationLetter
        fields = [
            'participant_name',
            'passport_number',
            'country_of_origin',
            'embassy_address',
        ]
        widgets = {
            'embassy_address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'

        self.helper.layout = Layout(
            HTML('<h3 class="font-bold text-xl mb-4">Personal Information</h3>'),
            Div(
                Div(
                    Field('participant_name', wrapper_class='mb-4'),
                    Field('passport_number', wrapper_class='mb-4'),
                    css_class='md:col-span-1'
                ),
                Div(
                    Field('country_of_origin', wrapper_class='mb-4'),
                    Field('email', wrapper_class='mb-4'),
                    css_class='md:col-span-1'
                ),
                css_class='grid md:grid-cols-2 gap-6'
            ),

            HTML('<h3 class="font-bold text-xl mb-4 mt-8">Embassy Information</h3>'),
            Field('embassy_address', wrapper_class='mb-4'),
            HTML(
                '<p class="text-sm text-gray-500">Please provide the complete address of the South African Embassy/Consulate where you will submit your visa application</p>'),

            Div(
                Submit('submit', 'Request Visa Letter', css_class='btn mt-6'),
                css_class='mt-8'
            ),

            HTML('<div class="mt-6 bg-yellow-50 border border-yellow-200 p-4 rounded-lg">' +
                 '<p class="text-sm text-yellow-800">Note: Your visa letter request will be reviewed by our team. ' +
                 'Once approved, the visa letter will be sent to your email address.</p></div>'),
        )
