from django.views.generic import TemplateView
from accounts.forms import CustomUserForm, UserProfileForm, SettingsForm
from accounts.models import UserProfile, Settings

class HomeView(TemplateView):
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ["home/home_logged_in.html"]
        else:
            return ["home/home_logged_out.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            settings, _ = Settings.objects.get_or_create(user=user)
            context['user_form'] = CustomUserForm(instance=user)
            context['user_profile_form'] = UserProfileForm(instance=user_profile)
            context['settings_form'] = SettingsForm(instance=settings)

            profile_fields = [
                'first_name', 'last_name',
                'bio', 'profile_picture', 'address', 'country', 'county_region', 'postal_code'
            ]
            settings_fields = ['currency', 'timezone', 'language', 'color_theme']
            context['total_fields'] = len(profile_fields) + len(settings_fields)
        return context