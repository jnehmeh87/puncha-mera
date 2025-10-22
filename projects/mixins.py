from accounts.models import Membership

class OrganizationPermissionMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()
            
        try:
            membership = Membership.objects.get(user=user)
            organization = membership.organization
            queryset = queryset.filter(organization=organization)
        except Membership.DoesNotExist:
            queryset = queryset.none()
        return queryset