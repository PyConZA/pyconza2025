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
            'email',
            'registration_type',
            'arrival_date',
            'departure_date',
            'is_speaker',
            'presentation_title',
            'embassy_address',
        ]
        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date',
                                                   'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'departure_date': forms.DateInput(attrs={'type': 'date',
                                                     'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
            'embassy_address': forms.Textarea(attrs={'rows': 3,
                                                     'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'

        for field_name, field in self.fields.items():
            if field_name != 'is_speaker':
                field.widget.attrs[
                    'class'] = 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500'

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

            HTML('<h3 class="font-bold text-xl mb-4 mt-8">Travel Information</h3>'),
            Div(
                Div(
                    Field('registration_type', wrapper_class='mb-4'),
                    Field('arrival_date', wrapper_class='mb-4'),
                    css_class='md:col-span-1'
                ),
                Div(
                    Field('departure_date', wrapper_class='mb-4'),
                    Div(
                        Field('is_speaker', wrapper_class='inline'),
                        HTML(
                            '<label for="id_is_speaker" class="ml-2">I am a speaker/presenter at PyCon Africa 2025</label>'),
                        css_class='flex items-center mb-4'
                    ),
                    Div(
                        Field('presentation_title', wrapper_class='mb-4'),
                        css_class='presenter-field hidden',
                        css_id='presentation-field'
                    ),
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

            HTML('''
            <script type="text/javascript">
                document.addEventListener("DOMContentLoaded", function() {
                    const arrivalDateInput = document.getElementById("id_arrival_date");
                    const departureDateInput = document.getElementById("id_departure_date");
                    
                    function validateDates() {
                        if (arrivalDateInput.value && departureDateInput.value) {
                            const arrivalDate = new Date(arrivalDateInput.value);
                            const departureDate = new Date(departureDateInput.value);
                            
                            if (arrivalDate > departureDate) {
                                departureDateInput.setCustomValidity("Departure date must be after arrival date");
                                return false;
                            } else {
                                departureDateInput.setCustomValidity("");
                                return true;
                            }
                        }
                        return true;
                    }
                    
                    arrivalDateInput.addEventListener("change", validateDates);
                    departureDateInput.addEventListener("change", validateDates);
                    
                    const isSpeakerCheckbox = document.getElementById("id_is_speaker");
                    const presentationField = document.getElementById("presentation-field");
                    
                    function togglePresentationField() {
                        if (isSpeakerCheckbox.checked) {
                            presentationField.classList.remove("hidden");
                        } else {
                            presentationField.classList.add("hidden");
                        }
                    }
                    
                    isSpeakerCheckbox.addEventListener("change", togglePresentationField);
                    togglePresentationField();
                });
            </script>
            ''')
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('is_speaker') and not cleaned_data.get('presentation_title'):
            self.add_error('presentation_title', 'Please provide the presentation title for speakers.')

        arrival_date = cleaned_data.get('arrival_date')
        departure_date = cleaned_data.get('departure_date')

        import datetime
        valid_start = datetime.date(2025, 10, 3)
        valid_end = datetime.date(2025, 10, 20)

        if arrival_date:
            if arrival_date < valid_start or arrival_date > valid_end:
                self.add_error('arrival_date', 'Arrival date must be between October 3-20, 2025.')

        if departure_date:
            if departure_date < valid_start or departure_date > valid_end:
                self.add_error('departure_date', 'Departure date must be between October 3-20, 2025.')

        if arrival_date and departure_date and arrival_date > departure_date:
            self.add_error('departure_date', 'Departure date must be after arrival date.')

        return cleaned_data
