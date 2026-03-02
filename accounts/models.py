import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    county_region = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Settings(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=100, default='UTC')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default='en')
    color_theme = models.CharField(max_length=20, default='blue')

    def __str__(self):
        return f"{self.user.username}'s Settings"

class Organization(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Membership(models.Model):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f'{self.user.username} - {self.organization.name} ({self.role})'

class Invitation(models.Model):
    email = models.EmailField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=Membership.ROLE_CHOICES)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f'Invitation for {self.email} to {self.organization.name}'

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
    archived = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
