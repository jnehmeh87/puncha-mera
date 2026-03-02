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

        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            
            # Admins/Owners can delete any entry in org, regular users only their own
            if membership.role in ['admin', 'owner']:
                entries_to_delete = TimeEntry.objects.filter(id__in=entry_ids, organization=organization)
            else:
                entries_to_delete = TimeEntry.objects.filter(id__in=entry_ids, user=user, organization=organization)
                
            count = entries_to_delete.count()
            entries_to_delete.delete()
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Successfully deleted {count} entries'
            })
            
        except Membership.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User has no organization'}, status=403)
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid request data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)