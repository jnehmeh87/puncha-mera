from django.db import models
from projects.models import Project
from accounts.models import CustomUser, Organization
import datetime

class TimeEntry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='time_entry_images/', blank=True, null=True)
    pause_duration = models.DurationField(default=datetime.timedelta(0))

    def __str__(self):
        return f'{self.user.username} - {self.project.name} ({self.date})'

    @property
    def duration(self):
        if self.end_time and self.start_time:
            # This is a bit tricky because start_time and end_time can cross midnight
            # For simplicity, we assume they are on the same day
            start_datetime = datetime.datetime.combine(self.date, self.start_time)
            end_datetime = datetime.datetime.combine(self.date, self.end_time)
            if end_datetime < start_datetime:
                end_datetime += datetime.timedelta(days=1)
            return end_datetime - start_datetime
        return None