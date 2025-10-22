from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import TimeEntry
from .forms import TimeEntryForm
from projects.mixins import OrganizationPermissionMixin

class TimeEntryListView(OrganizationPermissionMixin, ListView):
    model = TimeEntry
    template_name = 'time_entries/time_entry_list.html'
    context_object_name = 'time_entries'

    def get_queryset(self):
        return TimeEntry.objects.filter(user=self.request.user)

class TimeEntryDetailView(OrganizationPermissionMixin, DetailView):
    model = TimeEntry
    template_name = 'time_entries/time_entry_detail.html'

class TimeEntryCreateView(OrganizationPermissionMixin, CreateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = 'time_entries/time_entry_form.html'
    success_url = reverse_lazy('time_entries:time_entry-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TimeEntryUpdateView(OrganizationPermissionMixin, UpdateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = 'time_entries/time_entry_form.html'
    success_url = reverse_lazy('time_entries:time_entry-list')

class TimeEntryDeleteView(OrganizationPermissionMixin, DeleteView):
    model = TimeEntry
    template_name = 'time_entries/time_entry_confirm_delete.html'
    success_url = reverse_lazy('time_entries:time_entry-list')