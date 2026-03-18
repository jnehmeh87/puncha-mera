from django.db import models
from django.conf import settings
from projects.models import Project
from accounts.models import Organization
import datetime

# Create your models here.

class TimerSession(models.Model):
    STATUS_CHOICES = [
        ('RUNNING', 'Running'),
        ('PAUSED', 'Paused'),
        ('DRAFT', 'Draft'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='timer_sessions')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_timers')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_running = models.BooleanField(default=False)
    
    start_time = models.DateTimeField(null=True, blank=True)
    pause_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    accumulated_time = models.DurationField(default=datetime.timedelta(0))
    
    activity_log = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.status})"
