from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('basic/', views.BasicAnalyticsView.as_view(), name='basic'),
    path('advanced/', views.AdvancedAnalyticsView.as_view(), name='advanced'),
]
