import io
import datetime
import openpyxl
from decimal import Decimal

from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from time_entries.models import TimeEntry
from time_entries.templatetags.time_filters import format_duration
from .forms import ReportFilterForm

class ReportBaseView(LoginRequiredMixin, View):
    def get_filtered_queryset(self):
        user = self.request.user
        form = ReportFilterForm(self.request.GET or None, user=user)

        memberships = user.memberships.all()
        orgs_admin = [m.organization for m in memberships if m.role in ['admin', 'owner']]
        orgs_member = [m.organization for m in memberships if m.role not in ['admin', 'owner']]

        entries_admin = TimeEntry.objects.filter(organization__in=orgs_admin)
        entries_member = TimeEntry.objects.filter(organization__in=orgs_member, user=user)
        queryset = (entries_admin | entries_member).distinct().order_by('-date', '-start_time')

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
                
        return queryset, form

class ReportDashboardView(ReportBaseView, TemplateView):
    template_name = 'reports/report_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        queryset, form = self.get_filtered_queryset()
        context['form'] = form

        total_seconds = 0
        revenue_by_currency = {}
        
        for entry in queryset:
            dur = entry.actual_duration
            if dur:
                total_seconds += dur.total_seconds()
                
            earnings = entry.earnings
            if earnings > 0:
                currency = entry.project.currency
                if currency not in revenue_by_currency:
                    revenue_by_currency[currency] = Decimal('0.00')
                revenue_by_currency[currency] += earnings

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        total_hours_formatted = f"{hours}h {minutes}m {seconds}s"

        context['time_entries'] = queryset
        context['total_hours_formatted'] = total_hours_formatted
        context['revenue_by_currency'] = revenue_by_currency
        
        return context

class ExportExcelView(ReportBaseView):
    def get(self, request, *args, **kwargs):
        queryset, _ = self.get_filtered_queryset()
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Time Entries Report"
        
        headers = ['Date', 'Project', 'User', 'Title', 'Pause', 'Duration', 'Est. Revenue', 'Currency', 'Description', 'Notes']
        ws.append(headers)
        
        for entry in queryset:
            ws.append([
                entry.date.strftime('%Y-%m-%d'),
                entry.project.name,
                entry.user.username,
                entry.title,
                format_duration(entry.pause_duration),
                format_duration(entry.actual_duration),
                float(entry.earnings),
                entry.project.currency,
                entry.description,
                entry.notes
            ])
            
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="time_report.xlsx"'
        wb.save(response)
        return response

class ExportPdfView(ReportBaseView):
    def get(self, request, *args, **kwargs):
        queryset, _ = self.get_filtered_queryset()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="time_report.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph("Time Entries Report", styles['Title']))
        
        data = [['Date', 'Project', 'User', 'Title', 'Pause', 'Duration', 'Revenue']]
        for entry in queryset:
            revenue_str = f"{entry.earnings} {entry.project.currency}"
            data.append([
                entry.date.strftime('%Y-%m-%d'),
                entry.project.name[:15] + "..." if len(entry.project.name) > 15 else entry.project.name,
                entry.user.username,
                entry.title[:20] + "..." if len(entry.title) > 20 else entry.title,
                format_duration(entry.pause_duration),
                format_duration(entry.actual_duration),
                revenue_str
            ])
            
        table = Table(data, colWidths=[65, 95, 75, 120, 50, 60, 75])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        return response
