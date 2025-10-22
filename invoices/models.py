from django.db import models
from accounts.models import Organization

class Invoice(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    contact = models.ForeignKey('accounts.Contact', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20)
    issue_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.description