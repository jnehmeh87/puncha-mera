from django.urls import path
from .views import (
    ProjectListView, 
    ProjectCreateView, 
    ProjectDetailView,
    ProjectUpdateView,
    ProjectDeleteView,
    archive_project,
    unarchive_project,
    ProjectAddMemberView,
    ProjectUpdateMemberView
)

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name='project-list'),
    path('create/', ProjectCreateView.as_view(), name='project-create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:pk>/update/', ProjectUpdateView.as_view(), name='project-update'),
    path('<int:pk>/delete/', ProjectDeleteView.as_view(), name='project-delete'),
    path('<int:pk>/archive/', archive_project, name='project-archive'),
    path('<int:pk>/unarchive/', unarchive_project, name='project-unarchive'),
    path('<int:project_pk>/add-member/', ProjectAddMemberView.as_view(), name='project-add-member'),
    path('member/<int:pk>/update/', ProjectUpdateMemberView.as_view(), name='project-update-member'),
]