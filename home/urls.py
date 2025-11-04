from django.urls import path
from .views import HomeView, create_organization_from_tutorial, create_contact_from_tutorial, create_project_from_tutorial

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('create-organization-from-tutorial/', create_organization_from_tutorial, name='create_organization_from_tutorial'),
    path('create-contact-from-tutorial/', create_contact_from_tutorial, name='create_contact_from_tutorial'),
    path('create-project-from-tutorial/', create_project_from_tutorial, name='create_project_from_tutorial'),
]