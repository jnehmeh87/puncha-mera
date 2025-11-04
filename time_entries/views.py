from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import TimeEntry
from .forms import TimeEntryForm
from accounts.mixins import OrganizationPermissionMixin
from accounts.models import Membership

class TimeEntryListView(LoginRequiredMixin, ListView):
    model = TimeEntry
    template_name = 'time_entries/time_entry_list.html'
    context_object_name = 'time_entries'

    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return TimeEntry.objects.none()

        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            
            if membership.role in ['admin', 'owner']:
                return TimeEntry.objects.filter(organization=organization)
            else:
                return TimeEntry.objects.filter(user=user, organization=organization)
        except Membership.DoesNotExist:
            return TimeEntry.objects.none()

class TimeEntryDetailView(LoginRequiredMixin, DetailView):
    model = TimeEntry
    template_name = 'time_entries/time_entry_detail.html'

    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return TimeEntry.objects.none()

        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            
            if membership.role in ['admin', 'owner']:
                return TimeEntry.objects.filter(organization=organization)
            else:
                return TimeEntry.objects.filter(user=user, organization=organization)
        except Membership.DoesNotExist:
            return TimeEntry.objects.none()

class TimeEntryCreateView(LoginRequiredMixin, CreateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = 'time_entries/time_entry_form.html'
    success_url = reverse_lazy('time_entries:time_entry-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        membership = self.request.user.memberships.first()
        form.instance.organization = membership.organization
        return super().form_valid(form)

class TimeEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = 'time_entries/time_entry_form.html'
    success_url = reverse_lazy('time_entries:time_entry-list')

    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return TimeEntry.objects.none()

        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            
            if membership.role in ['admin', 'owner']:
                return TimeEntry.objects.filter(organization=organization)
            else:
                return TimeEntry.objects.filter(user=user, organization=organization)
        except Membership.DoesNotExist:
            return TimeEntry.objects.none()

class TimeEntryDeleteView(LoginRequiredMixin, DeleteView):
    model = TimeEntry
    template_name = 'time_entries/time_entry_confirm_delete.html'
    success_url = reverse_lazy('time_entries:time_entry-list')

    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return TimeEntry.objects.none()

        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            
            if membership.role in ['admin', 'owner']:
                return TimeEntry.objects.filter(organization=organization)
            else:
                return TimeEntry.objects.filter(user=user, organization=organization)
        except Membership.DoesNotExist:
            return TimeEntry.objects.none()