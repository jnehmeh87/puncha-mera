from django import forms
from .models import Project
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'contact']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            'contact',
        )
        self.helper.form_tag = False # Do not render form tags
