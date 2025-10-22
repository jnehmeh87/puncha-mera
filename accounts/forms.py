from django import forms
from .models import Membership, Organization

class InvitationForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=Membership.ROLE_CHOICES)

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name']