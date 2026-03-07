from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Sum, Count, F
from decimal import Decimal
import datetime
import json
from core.services import CurrencyConverter

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
        
        user_currency = self.request.user.settings.currency if hasattr(self.request.user, 'settings') else 'USD'

        # Currency Prefetching Optimization
        unique_dates = list({e.date for e in time_entries})
        unique_currencies = {p.currency for p in projects if hasattr(p, 'currency')}
        CurrencyConverter.prefetch_rates(unique_dates, unique_currencies, user_currency)

        total_seconds = sum([e.actual_duration.total_seconds() for e in time_entries if e.actual_duration])
        total_hours = round(total_seconds / 3600, 1)
        total_revenue = sum([
            CurrencyConverter.convert(float(e.earnings), e.date, getattr(e.project, 'currency', 'USD'), user_currency) 
            for e in time_entries
        ])
        
        # Chart logic based on period length
        days_to_plot = 7 if period == '7d' else 30
        now = timezone.now().date()
        date_range = [now - datetime.timedelta(days=i) for i in range(days_to_plot-1, -1, -1)]
        
        chart_labels = [d.strftime('%b %d') for d in date_range]
        chart_revenue_data = []
        chart_hours_data = []
        
        for day in date_range:
            day_entries = time_entries.filter(date=day)
            daily_revenue = sum([
                CurrencyConverter.convert(float(e.earnings), e.date, getattr(e.project, 'currency', 'USD'), user_currency) 
                for e in day_entries
            ])
            chart_revenue_data.append(float(daily_revenue))
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
        
        user_currency = self.request.user.settings.currency if hasattr(self.request.user, 'settings') else 'USD'
        
        # 0. Currency Prefetching Optimization
        # Gather all distinct dates and currencies in the current context
        unique_dates = list({e.date for e in time_entries})
        unique_currencies = {p.currency for p in projects if hasattr(p, 'currency')}
        CurrencyConverter.prefetch_rates(unique_dates, unique_currencies, user_currency)
        
        # --- Aggregation Variables ---
        total_billable_hours = 0.0
        total_non_billable_hours = 0.0
        total_revenue = 0.0
        
        # We will collect detailed data for charts
        client_revenue_map = {}
        chart_dates_map = {} # {date_str: {'rev': x, 'hours': y}}
        
        members_query = Membership.objects.filter(organization__in=valid_orgs).select_related('user')
        contacts = Project.objects.filter(organization__in=valid_orgs).values('contact__id', 'contact__name').distinct()
        
        unique_users = {m.user for m in members_query if m.user}
        team_performance_map = {u.id: {'name': u.get_full_name() or u.username, 'hours': 0, 'billable_hours': 0, 'revenue': 0, 'top_project': None, 'proj_map': {}} for u in unique_users}

        # First Pass: Aggregate all logic entry by entry to support multi-currency precisely
        for e in time_entries:
            hours = e.actual_duration.total_seconds() / 3600 if e.actual_duration else 0
            # Currency Conversion
            original_earnings = float(e.earnings)
            p_currency = getattr(e.project, 'currency', 'USD')
            converted_revenue = CurrencyConverter.convert(original_earnings, e.date, p_currency, user_currency)
            
            is_billable = original_earnings > 0
            if is_billable:
                total_billable_hours += hours
                total_revenue += converted_revenue
            else:
                total_non_billable_hours += hours
                
            # Chart Data: Revenue vs Hours
            date_str = e.date.strftime('%b %d')
            if date_str not in chart_dates_map:
                chart_dates_map[date_str] = {'rev': 0, 'hours': 0}
            chart_dates_map[date_str]['hours'] += hours
            chart_dates_map[date_str]['rev'] += converted_revenue if is_billable else 0

            # Chart Data: Revenue by Client
            client_name = e.project.contact.name if e.project and e.project.contact else "Internal/No Client"
            if is_billable:
                client_revenue_map[client_name] = client_revenue_map.get(client_name, 0) + converted_revenue
            
            # Team Performance Grid
            proj_name = e.project.name if e.project else "Unknown"
            if e.user and e.user.id in team_performance_map:
                u_id = e.user.id
                team_performance_map[u_id]['hours'] += hours
                if is_billable:
                    team_performance_map[u_id]['billable_hours'] += hours
                    team_performance_map[u_id]['revenue'] += converted_revenue
                team_performance_map[u_id]['proj_map'][proj_name] = team_performance_map[u_id]['proj_map'].get(proj_name, 0) + hours

        # --- Calculate KPIs ---
        total_hours = total_billable_hours + total_non_billable_hours
        utilization_rate = (total_billable_hours / total_hours * 100) if total_hours > 0 else 0
        avg_hourly_rate = (total_revenue / total_billable_hours) if total_billable_hours > 0 else 0

        # --- Finalize Team Performance List ---
        member_stats = []
        for u_id, data in team_performance_map.items():
            if data['hours'] > 0:
                top_proj = max(data['proj_map'], key=data['proj_map'].get)
                billable_pct = (data['billable_hours'] / data['hours'] * 100)
                member_stats.append({
                    'name': data['name'],
                    'total_hours': round(data['hours'], 1),
                    'billable_pct': round(billable_pct, 1),
                    'revenue': round(data['revenue'], 2),
                    'top_project': top_proj
                })
        member_stats = sorted(member_stats, key=lambda x: x['revenue'], reverse=True)

        # --- Finalize Dual Axis Chart (Revenue vs Hours) ---
        days_to_plot = 14 if period == '7d' else 30
        now = timezone.now().date()
        date_range = [now - datetime.timedelta(days=i) for i in range(days_to_plot-1, -1, -1)]
        bar_chart_labels = [d.strftime('%b %d') for d in date_range]
        bar_chart_revenue = [round(chart_dates_map.get(lbl, {}).get('rev', 0), 2) for lbl in bar_chart_labels]
        bar_chart_hours = [round(chart_dates_map.get(lbl, {}).get('hours', 0), 1) for lbl in bar_chart_labels]

        # --- Finalize Donut Chart (Client Revenue) ---
        sorted_clients = sorted(client_revenue_map.items(), key=lambda x: x[1], reverse=True)[:5]
        donut_labels = [k for k, v in sorted_clients]
        donut_data = [round(v, 2) for k, v in sorted_clients]

        # --- Finalize Weekly Progress Bars ---
        # Group time entries by week and calculate billable vs non-billable
        weekly_stats = []
        # Calculate exactly week 1, 2, 3 backwards from now based on the query period
        weeks = 2 if period == '7d' else 4
        for w in range(weeks):
            w_start = now - datetime.timedelta(days=(w*7)+6)
            w_end = now - datetime.timedelta(days=(w*7))
            w_entries = time_entries.filter(date__range=[w_start, w_end])
            
            w_bill = sum([(e.actual_duration.total_seconds()/3600) for e in w_entries if e.actual_duration and e.earnings > 0])
            w_non = sum([(e.actual_duration.total_seconds()/3600) for e in w_entries if e.actual_duration and e.earnings <= 0])
            w_tot = w_bill + w_non
            
            if w_tot > 0:
                weekly_stats.append({
                    'label': f'Week of {w_start.strftime("%b %d")}',
                    'billable_pct': round((w_bill / w_tot) * 100, 1),
                    'non_billable_pct': round((w_non / w_tot) * 100, 1)
                })
        weekly_stats.reverse()

        # UI Dropdowns
        period_options = [
            {'val': '7d', 'label': 'Last 7 Days', 'selected': period == '7d'},
            {'val': '30d', 'label': 'Last 30 Days', 'selected': period == '30d'},
            {'val': '90d', 'label': 'Last 90 Days', 'selected': period == '90d'},
            {'val': '1y', 'label': 'Last 1 Year', 'selected': period == '1y'},
            {'val': 'all', 'label': 'All Time', 'selected': period == 'all'}
        ]
        org_id_get = self.request.GET.get('org', '')
        org_list = [{'id': o.id, 'name': o.name, 'selected': str(o.id) == org_id_get} for o in valid_orgs]
        
        member_id_get = self.request.GET.get('member', '')
        member_list = []
        seen_user_ids = set()
        for m in members_query:
            mid = m.user.id if m.user else m.id
            if mid not in seen_user_ids:
                seen_user_ids.add(mid)
                name = m.user.get_full_name() if m.user and m.user.get_full_name() else (m.user.username if m.user else m.get_full_name() or m.username)
                member_list.append({'id': mid, 'name': name, 'selected': str(mid) == member_id_get})
            
        contact_id_get = self.request.GET.get('contact', '')
        contact_list = [{'id': c['contact__id'], 'name': c['contact__name'], 'selected': str(c['contact__id']) == contact_id_get} for c in contacts if c.get('contact__id')]

        context.update({
            # KPIs
            'total_billable_hours': round(total_billable_hours, 1),
            'total_non_billable_hours': round(total_non_billable_hours, 1),
            'total_revenue': round(total_revenue, 2),
            'avg_hourly_rate': round(avg_hourly_rate, 2),
            'utilization_rate': round(utilization_rate, 1),
            'user_currency': user_currency,
            
            # Chart Data
            'bar_chart_labels': bar_chart_labels,
            'bar_chart_revenue': bar_chart_revenue,
            'bar_chart_hours': bar_chart_hours,
            'donut_labels': donut_labels,
            'donut_data': donut_data,
            'weekly_stats': weekly_stats,
            
            # Table Data
            'member_stats': member_stats,
            
            # Dropdowns
            'period_options': period_options,
            'valid_orgs': org_list,
            'members': member_list,
            'contacts': contact_list,
            'current_period': period,
        })

        
        return context
