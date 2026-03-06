from django.core.exceptions import PermissionDenied
from .models import ProjectMember
from accounts.models import Membership

class ProjectMemberPermissionMixin:
    def has_permission(self):
        project = self.get_object()
        try:
            membership = Membership.objects.filter(user=self.request.user, organization=project.organization).first()
            if not membership:
                return False
                
            if membership.role in ['admin', 'owner']:
                return True
                
            member = ProjectMember.objects.get(project=project, user=self.request.user)
            if self.request.method == 'GET':
                return member.can_view
            elif self.request.method in ['POST', 'PUT', 'PATCH']:
                return member.can_edit
            elif self.request.method == 'DELETE':
                return member.can_delete
        except ProjectMember.DoesNotExist:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
