from django.db import models
from accounts.models import Organization

class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    contact = models.ForeignKey('accounts.Contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name