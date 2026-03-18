from django.urls import path
from . import views

app_name = 'time_entries'

urlpatterns = [
    path('', views.TimeEntryListView.as_view(), name='time_entry-list'),
    path('new/', views.TimeEntryCreateView.as_view(), name='time_entry-create'),
    path('<int:pk>/', views.TimeEntryDetailView.as_view(), name='time_entry-detail'),
    path('<int:pk>/edit/', views.TimeEntryUpdateView.as_view(), name='time_entry-update'),
    path('<int:pk>/delete/', views.TimeEntryDeleteView.as_view(), name='time_entry-delete'),
    path('<int:pk>/archive/', views.archive_time_entry, name='time_entry-archive'),
    path('<int:pk>/unarchive/', views.unarchive_time_entry, name='time_entry-unarchive'),
    path('bulk-delete/', views.bulk_delete_entries, name='time_entry-bulk-delete'),
]
