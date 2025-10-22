from django.db import models
from projects.models import Project
from accounts.models import CustomUser, Organization

class TimeEntry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='time_entry_images/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.project.name} ({self.start_time.date()})'

    @property
    def duration(self):
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None