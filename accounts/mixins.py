from django.core.exceptions import PermissionDenied
from .models import Membership

class AdminOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        organization_pk = self.kwargs.get('organization_pk')
        if not organization_pk:
            raise PermissionDenied("Organization not found.")

        membership = Membership.objects.filter(user=request.user, organization_id=organization_pk).first()
        if not membership or membership.role not in ['admin', 'owner']:
            raise PermissionDenied("You do not have permission to perform this action.")
        
        return super().dispatch(request, *args, **kwargs)