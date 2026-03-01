from django import forms
from projects.models import Project
from accounts.models import Contact, Organization
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

class ReportFilterForm(forms.Form):
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
                Column('organization', css_class='form-group col-md-4 mb-3'),
                Column('client', css_class='form-group col-md-4 mb-3'),
                Column('project', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('start_date', css_class='form-group col-md-4 mb-3'),
                Column('end_date', css_class='form-group col-md-4 mb-3'),
                Column(Submit('submit', 'Filter', css_class='btn btn-primary w-100 mt-4'), css_class='form-group col-md-4 mb-3 d-flex align-items-end'),
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
