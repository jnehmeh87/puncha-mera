from django.contrib.auth.mixins import AccessMixin
from .models import Membership, Invitation

class AdminOwnerRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        organization_pk = self.kwargs.get('organization_pk')
        if not organization_pk:
            invitation = Invitation.objects.get(pk=self.kwargs.get('pk'))
            organization_pk = invitation.organization.pk

        membership = Membership.objects.filter(user=request.user, organization_id=organization_pk).first()
        
        if not (membership and (membership.role == 'admin' or membership.role == 'owner')):
            return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)

class OrganizationPermissionMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        try:
            membership = Membership.objects.get(user=request.user)
            # Further checks can be added here if needed
        except Membership.DoesNotExist:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)