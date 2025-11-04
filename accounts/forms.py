from django import forms
from django.contrib.auth import get_user_model
from .models import Membership, Organization, UserProfile, Settings
import pycountry
import pytz

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