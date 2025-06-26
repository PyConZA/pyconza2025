from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML, Submit
from django import forms
from django_countries.widgets import CountrySelectWidget

from visa.models import VisaInvitationLetter


class VisaLetterForm(forms.ModelForm):
    class Meta:
        model = VisaInvitationLetter
        fields = [
            "full_name",
            "passport_number",
            "country_of_origin",
            "embassy_address",
        ]
        widgets = {
            "country_of_origin": CountrySelectWidget(
                attrs={
                    "class": "hidden",
                    "id": "country-select",
                }
            ),
            "embassy_address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "space-y-6"

        self.helper.layout = Layout(
            HTML('<h3 class="font-bold text-xl mb-4">Personal Information</h3>'),
            Div(
                Div(
                    Field("full_name", wrapper_class="mb-4"),
                    Field("passport_number", wrapper_class="mb-4"),
                    css_class="md:col-span-1",
                ),
                Div(
                    HTML('<div class="mb-4">'),
                    HTML(
                        '<label class="block text-sm font-medium text-gray-700 mb-2">Country of Origin <span class="text-red-600">*</span></label>'
                    ),
                    HTML('<div class="relative">'),
                    HTML(
                        '<input type="text" id="country-search" placeholder="Type to search countries..." class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500" autocomplete="off" />'
                    ),
                    HTML(
                        '<div id="country-dropdown" class="absolute z-10 w-full bg-white border border-gray-300 rounded-lg mt-1 max-h-60 overflow-y-auto hidden shadow-lg"></div>'
                    ),
                    HTML("</div>"),
                    HTML("</div>"),
                    css_class="md:col-span-1",
                ),
                css_class="grid md:grid-cols-2 gap-6",
            ),
            HTML('<h3 class="font-bold text-xl mb-4 mt-8">Embassy Information</h3>'),
            Field("embassy_address", wrapper_class="mb-4"),
            HTML(
                '<p class="text-sm text-gray-500">'
                "Please provide the complete address of the South African"
                "Embassy/Consulate where you will submit your visa application</p>"
            ),
            Div(
                Submit("submit", "Request Visa Letter", css_class="btn mt-6"),
                css_class="mt-8",
            ),
            HTML(
                '<div class="mt-6 bg-yellow-50 border border-yellow-200 p-4 rounded-lg">'
                + '<p class="text-sm text-yellow-800">Note: Your visa letter request will be reviewed by our team. '
                + "Once approved, the visa letter will be sent to your email address.</p></div>"
            ),
            Field("country_of_origin", wrapper_class="hidden"),
            HTML(
                """
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                const searchInput = document.getElementById('country-search');
                const dropdown = document.getElementById('country-dropdown');
                const hiddenSelect = document.getElementById('country-select');
                
                if (searchInput && dropdown && hiddenSelect) {
                    const countries = Array.from(hiddenSelect.options)
                        .filter(option => option.value !== '')
                        .map(option => ({
                            value: option.value,
                            text: option.text
                        }));
                    
                    let filteredCountries = countries;
                    let selectedIndex = -1;
                    
                    function renderDropdown() {
                        dropdown.innerHTML = '';
                        
                        filteredCountries.forEach((country, index) => {
                            const div = document.createElement('div');
                            div.className = `px-3 py-2 cursor-pointer hover:bg-blue-50 ${index === selectedIndex ? 'bg-blue-100' : ''}`;
                            div.textContent = country.text;
                            div.addEventListener('click', function() {
                                selectCountry(country);
                            });
                            dropdown.appendChild(div);
                        });
                        
                        if (filteredCountries.length === 0) {
                            const div = document.createElement('div');
                            div.className = 'px-3 py-2 text-gray-500';
                            div.textContent = 'No countries found';
                            dropdown.appendChild(div);
                        }
                    }
                    
                    function selectCountry(country) {
                        searchInput.value = country.text;
                        hiddenSelect.value = country.value;
                        dropdown.classList.add('hidden');
                        selectedIndex = -1;
                        
                        hiddenSelect.dispatchEvent(new Event('change'));
                    }
                    
                    searchInput.addEventListener('input', function() {
                        const searchTerm = this.value.toLowerCase();
                        filteredCountries = countries.filter(country => 
                            country.text.toLowerCase().includes(searchTerm)
                        );
                        selectedIndex = -1;
                        renderDropdown();
                        dropdown.classList.remove('hidden');
                    });
                    
                    searchInput.addEventListener('focus', function() {
                        filteredCountries = countries;
                        renderDropdown();
                        dropdown.classList.remove('hidden');
                    });
                    
                    searchInput.addEventListener('keydown', function(e) {
                        if (e.key === 'ArrowDown') {
                            e.preventDefault();
                            selectedIndex = Math.min(selectedIndex + 1, filteredCountries.length - 1);
                            renderDropdown();
                        } else if (e.key === 'ArrowUp') {
                            e.preventDefault();
                            selectedIndex = Math.max(selectedIndex - 1, -1);
                            renderDropdown();
                        } else if (e.key === 'Enter') {
                            e.preventDefault();
                            if (selectedIndex >= 0 && filteredCountries[selectedIndex]) {
                                selectCountry(filteredCountries[selectedIndex]);
                            }
                        } else if (e.key === 'Escape') {
                            dropdown.classList.add('hidden');
                            selectedIndex = -1;
                        }
                    });
                    
                    document.addEventListener('click', function(e) {
                        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
                            dropdown.classList.add('hidden');
                            selectedIndex = -1;
                        }
                    });
                    
                    if (hiddenSelect.value) {
                        const selectedCountry = countries.find(c => c.value === hiddenSelect.value);
                        if (selectedCountry) {
                            searchInput.value = selectedCountry.text;
                        }
                    }
                }
            });
            </script>
            """
            ),
        )
