from django.urls import path
from .views import SendInvitationView, AcceptInvitationView, CustomSignupView

app_name = 'accounts'

urlpatterns = [
    path('organization/<int:organization_pk>/invite/', SendInvitationView.as_view(), name='send-invitation'),
    path('invitation/accept/<uuid:token>/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('signup/', CustomSignupView.as_view(), name='account_signup'),
]