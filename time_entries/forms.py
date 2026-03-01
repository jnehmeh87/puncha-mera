from django import forms
from .models import TimeEntry
from projects.models import Project

class TimeEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TimeEntryForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['project'].queryset = Project.objects.filter(members=user)

    class Meta:
        model = TimeEntry
        fields = ['project', 'organization', 'title', 'date', 'start_time', 'end_time', 'description', 'notes', 'image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'step': '1'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'step': '1'}),
        }

from accounts.models import Contact, Organization, CustomUser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

class TimeEntryFilterForm(forms.Form):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.none(), 
        required=False, 
        empty_label="All Organizations",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    client = forms.ModelChoiceField(
        queryset=Contact.objects.none(), 
        required=False, 
        empty_label="All Clients",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(), 
        required=False, 
        empty_label="All Projects",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    member = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        required=False,
        empty_label="All Members",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('organization', css_class='form-group col-md-3 mb-3'),
                Column('client', css_class='form-group col-md-3 mb-3'),
                Column('project', css_class='form-group col-md-3 mb-3'),
                Column('member', css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column('start_date', css_class='form-group col-md-6 mb-0'),
                Column('end_date', css_class='form-group col-md-6 mb-0'),
            )
        )

        if user:
            # Filter dropdowns based on user's organizations
            memberships = user.memberships.all()
            organizations = Organization.objects.filter(members__in=memberships).distinct()
            self.fields['organization'].queryset = organizations

            if organizations.exists():
                self.fields['client'].queryset = Contact.objects.filter(organization__in=organizations)
                self.fields['project'].queryset = Project.objects.filter(organization__in=organizations)
                
                # Fetch members belonging to these organizations
                self.fields['member'].queryset = CustomUser.objects.filter(memberships__organization__in=organizations).distinct()
