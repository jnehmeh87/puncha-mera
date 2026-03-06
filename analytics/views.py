from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Sum, Count, F
from decimal import Decimal
import datetime
import json

from accounts.models import Membership
from time_entries.models import TimeEntry
from projects.models import Project

class AnalyticsFilterMixin:
    """Helper to process GET parameters for enterprise filtering."""
    def get_filtered_querysets(self):
        user = self.request.user
        memberships = Membership.objects.filter(user=user)
        
        if user.is_superuser:
            valid_orgs = [m.organization for m in memberships]
        else:
            valid_orgs = [m.organization for m in memberships if hasattr(m.organization, 'subscription') and m.organization.subscription.status == 'active']
            
        org_id = self.request.GET.get('org')
        if org_id:
            valid_orgs = [org for org in valid_orgs if str(org.id) == org_id]
            
        time_entries = TimeEntry.objects.filter(organization__in=valid_orgs)
        projects = Project.objects.filter(organization__in=valid_orgs)
        
        # Period Filtering
        period = self.request.GET.get('period', '30d')
        now = timezone.now().date()
        if period == '7d':
            start_date = now - datetime.timedelta(days=7)
        elif period == '30d':
            start_date = now - datetime.timedelta(days=30)
        elif period == '90d':
            start_date = now - datetime.timedelta(days=90)
        elif period == '1y':
            start_date = now - datetime.timedelta(days=365)
        else:
            start_date = None
            
        if start_date:
            time_entries = time_entries.filter(date__gte=start_date)
            
        # Member Filtering
        member_id = self.request.GET.get('member')
        if member_id:
            time_entries = time_entries.filter(user_id=member_id)
            
        # Contact (Client) Filtering
        contact_id = self.request.GET.get('contact')
        if contact_id:
            projects = projects.filter(contact_id=contact_id)
            time_entries = time_entries.filter(project__contact_id=contact_id)
            
        return time_entries, projects, valid_orgs, period, start_date

class AnalyticsPermissionMixin:
    """
    Mixin to check if the user has at least one valid organization.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        memberships = Membership.objects.filter(user=request.user)
        if not memberships.exists():
            raise PermissionDenied("You must belong to an organization to view analytics.")
            
        if not request.user.is_superuser:
            has_active = any(hasattr(m.organization, 'subscription') and m.organization.subscription.status == 'active' for m in memberships)
            if not has_active:
                 raise PermissionDenied("Active subscription required.")
        
        return super().dispatch(request, *args, **kwargs)

class BasicAnalyticsView(LoginRequiredMixin, AnalyticsPermissionMixin, AnalyticsFilterMixin, TemplateView):
    template_name = 'analytics/basic_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_entries, projects, valid_orgs, period, start_date = self.get_filtered_querysets()
        
        # Populate Filter Dropdowns
        members_query = Membership.objects.filter(organization__in=valid_orgs).select_related('user')
        contacts = Project.objects.filter(organization__in=valid_orgs).values('contact__id', 'contact__name').distinct()
        
        total_seconds = sum([e.actual_duration.total_seconds() for e in time_entries if e.actual_duration])
        total_hours = round(total_seconds / 3600, 1)
        total_revenue = sum([e.earnings for e in time_entries])
        
        # Chart logic based on period length
        days_to_plot = 7 if period == '7d' else 30
        now = timezone.now().date()
        date_range = [now - datetime.timedelta(days=i) for i in range(days_to_plot-1, -1, -1)]
        
        chart_labels = [d.strftime('%b %d') for d in date_range]
        chart_revenue_data = []
        chart_hours_data = []
        
        for day in date_range:
            day_entries = time_entries.filter(date=day)
            chart_revenue_data.append(float(sum([e.earnings for e in day_entries])))
            chart_hours_data.append(round(sum([e.actual_duration.total_seconds() for e in day_entries if e.actual_duration]) / 3600, 1))
            
        # Prepare Period Options
        period_options = [
            {'val': '7d', 'label': 'Last 7 Days', 'selected': period == '7d'},
            {'val': '30d', 'label': 'Last 30 Days', 'selected': period == '30d'},
            {'val': '90d', 'label': 'Last 90 Days', 'selected': period == '90d'},
            {'val': '1y', 'label': 'Last 1 Year', 'selected': period == '1y'},
            {'val': 'all', 'label': 'All Time', 'selected': period == 'all'}
        ]
        
        # Prepare valid_orgs for template
        org_id_get = self.request.GET.get('org', '')
        org_list = [{'id': o.id, 'name': o.name, 'selected': str(o.id) == org_id_get} for o in valid_orgs]
        
        # Prepare members for template
        member_id_get = self.request.GET.get('member', '')
        member_list = []
        seen_user_ids = set()
        for m in members_query:
            mid = m.user.id if m.user else m.id
            if mid not in seen_user_ids:
                seen_user_ids.add(mid)
                name = m.user.get_full_name() if m.user and m.user.get_full_name() else (m.user.username if m.user else m.get_full_name() or m.username)
                member_list.append({'id': mid, 'name': name, 'selected': str(mid) == member_id_get})
            
        # Prepare contacts for template
        contact_id_get = self.request.GET.get('contact', '')
        contact_list = [{'id': c['contact__id'], 'name': c['contact__name'], 'selected': str(c['contact__id']) == contact_id_get} for c in contacts if c.get('contact__id')]

        user_currency = self.request.user.settings.currency if hasattr(self.request.user, 'settings') else 'USD'

        context.update({
            'total_hours': total_hours,
            'total_revenue': total_revenue,
            'active_projects_count': projects.filter(archived=False).count(),
            'chart_labels': chart_labels,
            'chart_revenue_data': chart_revenue_data,
            'chart_hours_data': chart_hours_data,
            'period_options': period_options,
            'valid_orgs': org_list,
            'members': member_list,
            'contacts': contact_list,
            'current_period': period,
            'user_currency': user_currency,
        })
        return context

class AdvancedAnalyticsView(LoginRequiredMixin, AnalyticsPermissionMixin, AnalyticsFilterMixin, TemplateView):
    template_name = 'analytics/advanced_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_entries, projects, valid_orgs, period, start_date = self.get_filtered_querysets()
        
        members_query = Membership.objects.filter(organization__in=valid_orgs).select_related('user')
        contacts = Project.objects.filter(organization__in=valid_orgs).values('contact__id', 'contact__name').distinct()
        
        # 1. Member Performance
        member_stats = []
        unique_users = {m.user for m in members_query if m.user}
        for u in unique_users:
            u_entries = time_entries.filter(user=u)
            member_sec = sum([e.actual_duration.total_seconds() for e in u_entries if e.actual_duration])
            member_rev = sum([e.earnings for e in u_entries])
            
            member_stats.append({
                'name': u.get_full_name() or u.username,
                'hours': round(member_sec / 3600, 1),
                'revenue': float(member_rev)
            })
        member_stats = sorted(member_stats, key=lambda x: x['revenue'], reverse=True)
        
        # 2. Project Profitability
        project_stats = []
        for p in projects:
            p_entries = time_entries.filter(project=p)
            p_sec = sum([e.actual_duration.total_seconds() for e in p_entries if e.actual_duration])
            p_rev = sum([e.earnings for e in p_entries])
            if p_sec > 0 or p_rev > 0:
                project_stats.append({
                    'name': p.name,
                    'hours': round(p_sec / 3600, 1),
                    'revenue': float(p_rev),
                    'currency': getattr(p, 'currency', 'USD'),
                    'effective_rate': round(float(p_rev) / (p_sec / 3600), 2) if p_sec > 0 else 0
                })
        project_stats = sorted(project_stats, key=lambda x: x['effective_rate'], reverse=True)[:10]

        # 3. Client Breakdown Data (For Donut Chart)
        client_revenue = {}
        for e in time_entries:
            if e.project and e.project.contact:
                c_name = e.project.contact.name
                client_revenue[c_name] = client_revenue.get(c_name, 0) + float(e.earnings)
            else:
                client_revenue['Internal/No Client'] = client_revenue.get('Internal/No Client', 0) + float(e.earnings)
                
        # 4. Burn Rate Line Chart Data
        days_to_plot = 14 if period == '7d' else 30 # Plot more history for context
        now = timezone.now().date()
        date_range = [now - datetime.timedelta(days=i) for i in range(days_to_plot-1, -1, -1)]
        burn_labels = [d.strftime('%b %d') for d in date_range]
        burn_data = []
        for day in date_range:
            burn_data.append(float(sum([e.earnings for e in time_entries.filter(date=day)])))
            
        # Prepare Period Options
        period_options = [
            {'val': '7d', 'label': 'Last 7 Days', 'selected': period == '7d'},
            {'val': '30d', 'label': 'Last 30 Days', 'selected': period == '30d'},
            {'val': '90d', 'label': 'Last 90 Days', 'selected': period == '90d'},
            {'val': '1y', 'label': 'Last 1 Year', 'selected': period == '1y'},
            {'val': 'all', 'label': 'All Time', 'selected': period == 'all'}
        ]
        
        # Prepare valid_orgs for template
        org_id_get = self.request.GET.get('org', '')
        org_list = [{'id': o.id, 'name': o.name, 'selected': str(o.id) == org_id_get} for o in valid_orgs]
        
        # Prepare members for template
        member_id_get = self.request.GET.get('member', '')
        member_list = []
        seen_user_ids = set()
        for m in members_query:
            mid = m.user.id if m.user else m.id
            if mid not in seen_user_ids:
                seen_user_ids.add(mid)
                name = m.user.get_full_name() if m.user and m.user.get_full_name() else (m.user.username if m.user else m.get_full_name() or m.username)
                member_list.append({'id': mid, 'name': name, 'selected': str(mid) == member_id_get})
            
        # Prepare contacts for template
        contact_id_get = self.request.GET.get('contact', '')
        contact_list = [{'id': c['contact__id'], 'name': c['contact__name'], 'selected': str(c['contact__id']) == contact_id_get} for c in contacts if c.get('contact__id')]

        user_currency = self.request.user.settings.currency if hasattr(self.request.user, 'settings') else 'USD'

        context.update({
            'member_stats': member_stats,
            'project_stats': project_stats,
            'client_labels': list(client_revenue.keys()),
            'client_revenue_data': list(client_revenue.values()),
            'burn_labels': burn_labels,
            'burn_data': burn_data,
            'period_options': period_options,
            'valid_orgs': org_list,
            'members': member_list,
            'contacts': contact_list,
            'current_period': period,
            'user_currency': user_currency,
        })
        
        return context
