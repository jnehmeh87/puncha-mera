from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Project, ProjectMember
from .mixins import ProjectMemberPermissionMixin
from accounts.models import Membership, CustomUser

class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Project.objects.filter(members=user, deleted=False)
        return Project.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['active_projects'] = queryset.filter(archived=False)
        context['archived_projects'] = queryset.filter(archived=True)
        return context

class ProjectCreateView(CreateView):
    model = Project
    fields = ['name', 'contact', 'description']
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project-list')

    def form_valid(self, form):
        user = self.request.user
        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            form.instance.organization = organization
            response = super().form_valid(form)
            ProjectMember.objects.create(project=self.object, user=user, can_view=True, can_edit=True, can_delete=True)
            return response
        except Membership.DoesNotExist:
            return super().form_invalid(form)

class ProjectDetailView(ProjectMemberPermissionMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'

class ProjectUpdateView(ProjectMemberPermissionMixin, UpdateView):
    model = Project
    fields = ['name', 'contact', 'description']
    template_name = 'projects/project_form.html'

class ProjectDeleteView(ProjectMemberPermissionMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.deleted = True
        self.object.save()
        return redirect(self.get_success_url())

class ProjectAddMemberView(CreateView):
    model = ProjectMember
    fields = ['user', 'can_view', 'can_edit', 'can_delete']
    template_name = 'projects/project_add_member.html'

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.kwargs['project_pk']})

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        form.instance.project = project
        return super().form_valid(form)

class ProjectUpdateMemberView(UpdateView):
    model = ProjectMember
    fields = ['can_view', 'can_edit', 'can_delete']
    template_name = 'projects/project_update_member.html'

    def get_success_url(self):
        return reverse_lazy('projects:project-detail', kwargs={'pk': self.object.project.pk})

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