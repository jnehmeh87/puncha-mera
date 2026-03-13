from django.db import models
from django.conf import settings

class UserIncomeConfig(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='income_config')
    country = models.CharField(max_length=10, default='SE') # SE, GB, US, etc.
    base_gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    target_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    us_sales_tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username} - Income Config"

class MonthlyBookkeeping(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookkeeping_records')
    month = models.DateField() # Store the first day of the month, e.g. 2026-03-01
    
    # Financial snapshots
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vacation_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pension = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sick_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    overheads = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    social_contributions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'month')
        ordering = ['-month']

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%Y-%m')}"
