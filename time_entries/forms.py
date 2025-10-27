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
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
