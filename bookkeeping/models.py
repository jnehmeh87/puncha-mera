from django.db import models
from accounts.models import CustomUser, Organization
from invoices.models import Invoice

class Expense(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    date_incurred = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    vendor = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    receipt_image = models.ImageField(upload_to='bookkeeping/receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.receipt_image:
            from core.utils.image_compression import compress_image
            self.receipt_image = compress_image(self.receipt_image)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Expense: {self.vendor} - {self.amount} {self.currency} ({self.date_incurred})"

class Income(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    bank_registry_date = models.DateField()
    source = models.CharField(max_length=255, blank=True, help_text="e.g., Client name or Invoice Number")
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='incomes', help_text="Optional link to a generated invoice")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Income: {self.source} - {self.amount} {self.currency} ({self.bank_registry_date})"
