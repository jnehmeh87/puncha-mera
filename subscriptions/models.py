from django.db import models

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
    )

    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f'{self.organization} - {self.plan}'