from django import forms
from .models import Project, ProjectMember
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

COMMON_CURRENCIES = [
    ('USD', 'US Dollar (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('GBP', 'British Pound (GBP)'),
    ('CAD', 'Canadian Dollar (CAD)'),
    ('AUD', 'Australian Dollar (AUD)'),
    ('SEK', 'Swedish Krona (SEK)'),
    ('NOK', 'Norwegian Krone (NOK)'),
    ('DKK', 'Danish Krone (DKK)'),
    ('JPY', 'Japanese Yen (JPY)'),
    ('INR', 'Indian Rupee (INR)'),
]

class ProjectForm(forms.ModelForm):
    currency = forms.ChoiceField(choices=COMMON_CURRENCIES)

    class Meta:
        model = Project
        fields = ['name', 'description', 'contact', 'currency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            'contact',
            'currency',
        )
        self.helper.form_tag = False # Do not render form tags

class ProjectMemberForm(forms.ModelForm):
    class Meta:
        model = ProjectMember
        fields = ['user', 'hourly_rate', 'can_view', 'can_edit', 'can_delete']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'user',
            'hourly_rate',
            'can_view',
            'can_edit',
            'can_delete',
        )
        self.helper.form_tag = False
