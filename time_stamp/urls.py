from django.urls import path
from . import views

app_name = 'time_stamp'

urlpatterns = [
    path('', views.timer_view, name='timer'),
]
