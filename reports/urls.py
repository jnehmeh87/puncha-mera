from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportDashboardView.as_view(), name='dashboard'),
    path('export/excel/', views.ExportExcelView.as_view(), name='export-excel'),
    path('export/pdf/', views.ExportPdfView.as_view(), name='export-pdf'),
]
