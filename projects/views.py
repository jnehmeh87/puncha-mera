from django.views.generic import ListView, CreateView, DetailView
from .models import Project
from .mixins import OrganizationPermissionMixin
from accounts.models import Membership

class ProjectListView(OrganizationPermissionMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'

class ProjectCreateView(OrganizationPermissionMixin, CreateView):
    model = Project
    fields = ['name', 'contact', 'description']
    template_name = 'projects/project_form.html'

    def form_valid(self, form):
        user = self.request.user
        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            form.instance.organization = organization
        except Membership.DoesNotExist:
            # Handle case where user has no organization
            # You might want to redirect or show an error
            return super().form_invalid(form)
        return super().form_valid(form)

class ProjectDetailView(OrganizationPermissionMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'