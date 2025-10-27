from django.db import models
from django.urls import reverse
from accounts.models import Organization

class ProjectManager(models.Manager):
    def get_queryset(self):
        return super(ProjectManager, self).get_queryset().filter(deleted=False)

class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    contact = models.ForeignKey('accounts.Contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    archived = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    objects = ProjectManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:project-detail', kwargs={'pk': self.pk})