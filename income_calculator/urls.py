from django.urls import path
from . import views

app_name = 'income_calculator'

urlpatterns = [
    path('', views.income_calculator_dashboard, name='dashboard'),
    path('api/update-config/', views.update_income_config, name='update_config'),
    path('api/save-bookkeeping/', views.save_monthly_bookkeeping, name='save_bookkeeping'),
]
