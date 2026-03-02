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

COMMON_LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('de', 'German'),
    ('it', 'Italian'),
    ('pt', 'Portuguese'),
    ('nl', 'Dutch'),
    ('sv', 'Swedish'),
    ('no', 'Norwegian'),
    ('fi', 'Finnish'),
    ('da', 'Danish'),
    ('ru', 'Russian'),
    ('zh', 'Chinese'),
    ('ja', 'Japanese'),
    ('ko', 'Korean'),
    ('ar', 'Arabic'),
    ('hi', 'Hindi'),
    ('tr', 'Turkish'),
]

class SettingsForm(forms.ModelForm):
    COLOR_THEMES = [
        ('blue', 'Classic Blue'),
        ('green', 'Emerald Green'),
        ('purple', 'Deep Purple'),
        ('orange', 'Sunset Orange'),
        ('pink', 'Hot Pink'),
        ('red', 'Crimson Red'),
        ('teal', 'Ocean Teal'),
    ]
    
    currency = forms.ChoiceField(choices=[(currency.alpha_3, currency.name) for currency in pycountry.currencies])
    language = forms.ChoiceField(choices=COMMON_LANGUAGES)
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.all_timezones])
    color_theme = forms.ChoiceField(choices=COLOR_THEMES)

    class Meta:
        model = Settings
        exclude = ['user']

class CurrencyForm(forms.ModelForm):
    currency = forms.ChoiceField(choices=[(currency.alpha_3, currency.name) for currency in pycountry.currencies])
    class Meta:
        model = Settings
        fields = ['currency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('currency')
        self.helper.form_tag = False

class TimezoneForm(forms.ModelForm):
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.all_timezones])
    class Meta:
        model = Settings
        fields = ['timezone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('timezone')
        self.helper.form_tag = False

class LanguageForm(forms.ModelForm):
    language = forms.ChoiceField(choices=COMMON_LANGUAGES)
    class Meta:
        model = Settings
        fields = ['language']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('language')
        self.helper.form_tag = False

class ColorThemeForm(forms.ModelForm):
    color_theme = forms.ChoiceField(choices=COLOR_THEMES)
    class Meta:
        model = Settings
        fields = ['color_theme']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('color_theme')
        self.helper.form_tag = False