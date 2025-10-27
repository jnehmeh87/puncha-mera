from django.urls import path
from .views import (
    SendInvitationView, 
    AcceptInvitationView, 
    CustomSignupView,
    ContactListView,
    ContactCreateView,
    ContactDetailView,
    ContactUpdateView,
    ContactDeleteView,
    OrganizationListView,
    OrganizationDetailView,
    OrganizationCreateView,
    archive_contact,
    unarchive_contact,
    archive_organization,
    unarchive_organization
)

app_name = 'accounts'

urlpatterns = [
    path('organization/<int:organization_pk>/invite/', SendInvitationView.as_view(), name='send-invitation'),
    path('invitation/accept/<uuid:token>/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('signup/', CustomSignupView.as_view(), name='account_signup'),
    path('contacts/', ContactListView.as_view(), name='contact-list'),
    path('contacts/new/', ContactCreateView.as_view(), name='contact-create'),
    path('contacts/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
    path('contacts/<int:pk>/edit/', ContactUpdateView.as_view(), name='contact-update'),
    path('contacts/<int:pk>/delete/', ContactDeleteView.as_view(), name='contact-delete'),
    path('contacts/<int:pk>/archive/', archive_contact, name='contact-archive'),
    path('contacts/<int:pk>/unarchive/', unarchive_contact, name='contact-unarchive'),
    path('organizations/', OrganizationListView.as_view(), name='organization-list'),
    path('organizations/new/', OrganizationCreateView.as_view(), name='organization-create'),
    path('organizations/<int:pk>/', OrganizationDetailView.as_view(), name='organization-detail'),
    path('organizations/<int:pk>/archive/', archive_organization, name='organization-archive'),
    path('organizations/<int:pk>/unarchive/', unarchive_organization, name='organization-unarchive'),
]