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

        if not Membership.objects.filter(user=request.user).exists():
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_organizations(self):
        from .models import Organization
        return Organization.objects.filter(members__user=self.request.user, archived=False, deleted=False)