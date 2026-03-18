from django.urls import path
from . import views

app_name = 'time_stamp'

urlpatterns = [
    path('', views.timer_view, name='timer'),
    path('api/session/start/', views.start_timer_session, name='start_timer_session'),
    path('api/session/<int:session_id>/pause/', views.pause_timer_session, name='pause_timer_session'),
    path('api/session/<int:session_id>/resume/', views.resume_timer_session, name='resume_timer_session'),
    path('api/session/<int:session_id>/stop/', views.stop_timer_session, name='stop_timer_session'),
    path('api/session/<int:session_id>/delete/', views.delete_timer_session, name='delete_timer_session'),
    path('api/session/active/', views.get_active_sessions, name='get_active_sessions'),
    path('api/options/', views.get_timer_options, name='get_timer_options'),
]
