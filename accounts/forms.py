from django import forms
from .models import Membership, Organization, UserProfile, Settings

class InvitationForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=Membership.ROLE_CHOICES)

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user']

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude = ['user']