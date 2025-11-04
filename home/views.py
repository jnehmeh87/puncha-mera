from django.views.generic import TemplateView
from accounts.forms import CustomUserForm, UserProfileForm, SettingsForm, OrganizationForm, ContactForm
from projects.forms import ProjectForm
from accounts.models import UserProfile, Settings, Organization, Contact
from projects.models import Project
from django.http import JsonResponse
import json

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
            context['organization_form'] = OrganizationForm()
            context['contact_form'] = ContactForm()
            context['project_form'] = ProjectForm()

            profile_fields = [
                'first_name', 'last_name',
                'bio', 'profile_picture', 'address', 'country', 'county_region', 'postal_code'
            ]
            settings_fields = ['currency', 'timezone', 'language', 'color_theme']
            context['total_fields'] = len(profile_fields) + len(settings_fields)
        return context

def create_organization_from_tutorial(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.created_by = request.user
            organization.save()
            return JsonResponse({'success': True, 'message': 'Organization created successfully.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def create_contact_from_tutorial(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            # Assuming the user has created at least one organization
            # and we want to associate the contact with the first one
            organization = Organization.objects.filter(created_by=request.user).first()
            if organization:
                contact.organization = organization
                contact.save()
                return JsonResponse({'success': True, 'message': 'Contact created successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'No organization found for the user.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def create_project_from_tutorial(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            # Assuming the user has created at least one organization
            # and we want to associate the project with the first one
            organization = Organization.objects.filter(created_by=request.user).first()
            if organization:
                project.organization = organization
                project.save()
                return JsonResponse({'success': True, 'message': 'Project created successfully.'})
            else:
                return JsonResponse({'success': False, 'message': 'No organization found for the user.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
