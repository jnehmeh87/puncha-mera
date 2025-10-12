from django.db import models
from accounts.models import Organization

class Contact(models.Model):
    CONTACT_TYPE_CHOICES = (
        ('Category', 'Category'),
        ('Client', 'Client'),
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    company_email = models.EmailField(blank=True)
    company_address = models.CharField(max_length=255, blank=True)
    company_contact_person = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name