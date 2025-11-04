from django import forms
from django.contrib.auth import get_user_model
from .models import Membership, Organization, UserProfile, Settings, Contact
import pycountry
import pytz
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']

class InvitationForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=Membership.ROLE_CHOICES)

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
        )
        self.helper.form_tag = False # Do not render form tags

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'contact_type', 'company_email', 'company_address', 'company_contact_person']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'contact_type',
            'company_email',
            'company_address',
            'company_contact_person',
        )
        self.helper.form_tag = False # Do not render form tags

class UserProfileForm(forms.ModelForm):
    country = forms.ChoiceField(choices=[(country.name, country.name) for country in pycountry.countries])

    class Meta:
        model = UserProfile
        exclude = ['user']

class SettingsForm(forms.ModelForm):
    currency = forms.ChoiceField(choices=[(currency.alpha_3, currency.name) for currency in pycountry.currencies])
    language = forms.ChoiceField(choices=[(lang.alpha_3, lang.name) for lang in pycountry.languages])
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.all_timezones])

    class Meta:
        model = Settings
        exclude = ['user']