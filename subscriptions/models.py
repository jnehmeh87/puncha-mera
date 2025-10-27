from django.db import models
from accounts.models import Organization

class Feature(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=100)
    max_members = models.PositiveIntegerField()
    features = models.ManyToManyField(Feature)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('trialing', 'Trialing'),
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
    )

    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.organization} - {self.plan}'