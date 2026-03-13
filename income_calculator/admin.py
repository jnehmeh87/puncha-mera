from django.contrib import admin
from .models import UserIncomeConfig, MonthlyBookkeeping

@admin.register(UserIncomeConfig)
class UserIncomeConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'base_gross_salary')
    search_fields = ('user__username', 'user__email')

@admin.register(MonthlyBookkeeping)
class MonthlyBookkeepingAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'total_revenue', 'gross_salary')
    search_fields = ('user__username', 'user__email')
    list_filter = ('month',)
