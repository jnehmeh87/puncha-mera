from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import TimeEntry
from .forms import TimeEntryForm
from accounts.mixins import OrganizationPermissionMixin
from accounts.models import Membership
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.db.models import Sum, F
from django.utils import timezone
from django.core.paginator import Paginator

class TimeEntryListView(LoginRequiredMixin, ListView):
    model = TimeEntry
    template_name = 'time_entries/time_entry_list.html'
    context_object_name = 'time_entries'

    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return TimeEntry.objects.none()

        memberships = Membership.objects.filter(user=user)
        if not memberships.exists():
            return TimeEntry.objects.none()
            
        # Get all relevant entries across their organizations
        accessible_org_ids = [m.organization.id for m in memberships]
        org_roles = {m.organization.id: m.role for m in memberships}
        
        # Build query for the organizations
        queryset = TimeEntry.objects.filter(organization_id__in=accessible_org_ids)
        
        # Filter entries down to self if not an admin/owner for that org
        # For simplicity since this is generic to all orgs, if they are admin/owner in ANY
        # we still restrict to user=user for orgs they are mere 'members' of
        if not any(role in ['admin', 'owner'] for role in org_roles.values()):
            queryset = queryset.filter(user=user)

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
        
        queryset = self.get_queryset()
        context['active_entries'] = queryset.filter(archived=False)
        context['archived_entries'] = queryset.filter(archived=True)
        return context

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def archive_time_entry(request, pk):
    entry = get_object_or_404(TimeEntry, pk=pk)
    entry.archived = True
    entry.save()
    return redirect('time_entries:time_entry-list')

@login_required
def unarchive_time_entry(request, pk):
    entry = get_object_or_404(TimeEntry, pk=pk)
    entry.archived = False
    entry.save()
    return redirect('time_entries:time_entry-list')

class TimeEntryDetailView(LoginRequiredMixin, DetailView):
    model = TimeEntry
    template_name = 'time_entries/time_entry_detail.html'

    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return TimeEntry.objects.none()

        memberships = Membership.objects.filter(user=user)
        if not memberships.exists():
            return TimeEntry.objects.none()
            
        accessible_org_ids = [m.organization.id for m in memberships]
        org_roles = {m.organization.id: m.role for m in memberships}
        
        queryset = TimeEntry.objects.filter(organization_id__in=accessible_org_ids)
        if not any(role in ['admin', 'owner'] for role in org_roles.values()):
            queryset = queryset.filter(user=user)
            
        return queryset

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

        memberships = Membership.objects.filter(user=user)
        if not memberships.exists():
            return TimeEntry.objects.none()
            
        accessible_org_ids = [m.organization.id for m in memberships]
        org_roles = {m.organization.id: m.role for m in memberships}
        
        queryset = TimeEntry.objects.filter(organization_id__in=accessible_org_ids)
        if not any(role in ['admin', 'owner'] for role in org_roles.values()):
            queryset = queryset.filter(user=user)
            
        return queryset

class TimeEntryDeleteView(LoginRequiredMixin, DeleteView):
    model = TimeEntry
    template_name = 'time_entries/time_entry_confirm_delete.html'
    success_url = reverse_lazy('time_entries:time_entry-list')

    def get_queryset(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return TimeEntry.objects.none()

        memberships = Membership.objects.filter(user=user)
        if not memberships.exists():
            return TimeEntry.objects.none()
            
        accessible_org_ids = [m.organization.id for m in memberships]
        org_roles = {m.organization.id: m.role for m in memberships}
        
        queryset = TimeEntry.objects.filter(organization_id__in=accessible_org_ids)
        if not any(role in ['admin', 'owner'] for role in org_roles.values()):
            queryset = queryset.filter(user=user)
            
        return queryset

@require_POST
def bulk_delete_entries(request):
    try:
        data = json.loads(request.body)
        entry_ids = data.get('entry_ids', [])
        
        if not entry_ids:
            return JsonResponse({'status': 'error', 'message': 'No entries selected'})

        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

        memberships = Membership.objects.filter(user=user)
        if not memberships.exists():
            return JsonResponse({'status': 'error', 'message': 'User has no organization'}, status=403)
            
        accessible_org_ids = [m.organization.id for m in memberships]
        org_roles = {m.organization.id: m.role for m in memberships}
        
        if any(role in ['admin', 'owner'] for role in org_roles.values()):
            entries_to_delete = TimeEntry.objects.filter(id__in=entry_ids, organization_id__in=accessible_org_ids)
        else:
            entries_to_delete = TimeEntry.objects.filter(id__in=entry_ids, user=user, organization_id__in=accessible_org_ids)
            
        count = entries_to_delete.count()
        entries_to_delete.delete()
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Successfully deleted {count} entries'
        })
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)