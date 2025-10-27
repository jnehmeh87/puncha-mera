from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Project
from .mixins import OrganizationPermissionMixin
from accounts.models import Membership

class ProjectListView(OrganizationPermissionMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'

    def get_queryset(self):
        user = self.request.user
        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            return Project.objects.filter(organization=organization)
        except Membership.DoesNotExist:
            return Project.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['active_projects'] = queryset.filter(archived=False)
        context['archived_projects'] = queryset.filter(archived=True)
        return context

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

class ProjectUpdateView(OrganizationPermissionMixin, UpdateView):
    model = Project
    fields = ['name', 'contact', 'description']
    template_name = 'projects/project_form.html'

class ProjectDeleteView(OrganizationPermissionMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.deleted = True
        self.object.save()
        return redirect(self.get_success_url())

def archive_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.archived = True
    project.save()
    return redirect('projects:project-list')

def unarchive_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.archived = False
    project.save()
    return redirect('projects:project-list')