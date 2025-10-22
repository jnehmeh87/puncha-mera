from django.urls import path
from .views import (
    SendInvitationView, 
    AcceptInvitationView, 
    CustomSignupView,
    ContactListView,
    ContactCreateView,
    ContactDetailView,
    ContactUpdateView,
    ContactDeleteView
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
]