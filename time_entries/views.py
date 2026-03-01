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
                queryset = TimeEntry.objects.filter(organization=organization)
            else:
                queryset = TimeEntry.objects.filter(user=user, organization=organization)
        except Membership.DoesNotExist:
            return TimeEntry.objects.none()

        from .forms import TimeEntryFilterForm
        form = TimeEntryFilterForm(self.request.GET or None, user=user)
        
        if form.is_valid():
            org = form.cleaned_data.get('organization')
            if org:
                queryset = queryset.filter(organization=org)
            
            client = form.cleaned_data.get('client')
            if client:
                queryset = queryset.filter(project__contact=client)
                
            project = form.cleaned_data.get('project')
            if project:
                queryset = queryset.filter(project=project)
                
            member = form.cleaned_data.get('member')
            if member:
                queryset = queryset.filter(user=member)
                
            start_date = form.cleaned_data.get('start_date')
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
                
            end_date = form.cleaned_data.get('end_date')
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
                
        return queryset.order_by('-date', '-start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .forms import TimeEntryFilterForm
        context['form'] = TimeEntryFilterForm(self.request.GET or None, user=self.request.user)
        return context

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