from django.urls import path
from .views import (
    ProjectListView, 
    ProjectCreateView, 
    ProjectDetailView
)

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name='project-list'),
    path('create/', ProjectCreateView.as_view(), name='project-create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
]