from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from decimal import Decimal
from datetime import datetime, date
import calendar
from .models import UserIncomeConfig, MonthlyBookkeeping
from time_entries.models import TimeEntry
from core.services import CurrencyConverter

@login_required
def income_calculator_dashboard(request):
    """
    Renders the main income calculator dashboard.
    Fetches the user's config (or creates defaults) and current month's TimeEntries.
    """
    config, created = UserIncomeConfig.objects.get_or_create(user=request.user)

    # Get current month or selected month from request
    month_str = request.GET.get('month')
    if month_str:
        try:
            target_date = datetime.strptime(month_str, '%Y-%m').date()
            year = target_date.year
            month = target_date.month
        except ValueError:
            today = date.today()
            year = today.year
            month = today.month
    else:
        today = date.today()
        year = today.year
        month = today.month

    # Calculate date range for the selected month
    _, num_days = calendar.monthrange(year, month)
    first_day = date(year, month, 1)
    last_day = date(year, month, num_days)

    # Fetch TimeEntries for that month
    entries = TimeEntry.objects.filter(
        user=request.user,
        date__gte=first_day,
        date__lte=last_day
    ).select_related('project')

    # Calculate previous month's date range
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    _, prev_num_days = calendar.monthrange(prev_year, prev_month)
    prev_first_day = date(prev_year, prev_month, 1)
    prev_last_day = date(prev_year, prev_month, prev_num_days)

    prev_entries = TimeEntry.objects.filter(
        user=request.user,
        date__gte=prev_first_day,
        date__lte=prev_last_day
    ).select_related('project')

    user_currency = request.user.settings.currency if hasattr(request.user, 'settings') else 'USD'
    unique_dates = list({e.date for e in entries} | {pe.date for pe in prev_entries})
    unique_currencies = {getattr(e.project, 'currency', 'USD') for e in list(entries) + list(prev_entries)}
    CurrencyConverter.prefetch_rates(unique_dates, unique_currencies, user_currency)

    prev_total_revenue = Decimal('0.00')
    for pe in prev_entries:
        p_curr = getattr(pe.project, 'currency', 'USD')
        converted = CurrencyConverter.convert(float(pe.earnings), pe.date, p_curr, user_currency)
        prev_total_revenue += Decimal(str(converted))

    entries_data = []
    total_invoiced_excl_vat = Decimal('0.00')

    for entry in entries:
        p_curr = getattr(entry.project, 'currency', 'USD')
        converted_earnings = CurrencyConverter.convert(float(entry.earnings), entry.date, p_curr, user_currency)
        converted_decimal = Decimal(str(converted_earnings))
        
        entries_data.append({
            'id': entry.id,
            'title': entry.title,
            'project': entry.project.name,
            'date': entry.date.strftime('%Y-%m-%d'),
            'duration': entry.actual_duration.total_seconds() / 3600,
            'earnings': str(converted_decimal),
            'currency': user_currency
        })
        total_invoiced_excl_vat += converted_decimal

    # Convert config to dictionary to pass safely to JS
    config_data = {
        'country': config.country,
        'base_gross_salary': str(config.base_gross_salary),
        'target_profit_margin': str(config.target_profit_margin),
        'us_sales_tax': str(config.us_sales_tax),
    }

    # Pass historical bookkeeping records
    history = MonthlyBookkeeping.objects.filter(user=request.user).order_by('-month')

    context = {
        'config': config,
        'config_json': json.dumps(config_data),
        'entries_json': json.dumps(entries_data),
        'current_month_str': f"{year}-{month:02d}",
        'history': history,
        'total_revenue': total_invoiced_excl_vat,
        'prev_total_revenue': prev_total_revenue,
        'user_currency': user_currency,
    }
    return render(request, 'income_calculator/calculator.html', context)

@login_required
@require_POST
def update_income_config(request):
    """
    API endpoint to update user's base rate, country, or custom tax settings.
    """
    try:
        data = json.loads(request.body)
        config, created = UserIncomeConfig.objects.get_or_create(user=request.user)
        
        if 'country' in data:
            config.country = data['country']
        if 'base_gross_salary' in data:
            config.base_gross_salary = Decimal(str(data['base_gross_salary']))
        if 'target_profit_margin' in data:
            config.target_profit_margin = Decimal(str(data['target_profit_margin']))
        if 'us_sales_tax' in data:
            config.us_sales_tax = Decimal(str(data['us_sales_tax']))
            
        config.save()
        
        return JsonResponse({'status': 'success', 'message': 'Configuration saved successfully.'})
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def save_monthly_bookkeeping(request):
    """
    API endpoint to save a finalized month's projections to the registry.
    """
    try:
        data = json.loads(request.body)
        month_str = data.get('month') # expected format 'YYYY-MM'
        target_date = datetime.strptime(month_str, '%Y-%m').date()
        first_day = date(target_date.year, target_date.month, 1)

        # Update or create the snapshot
        bookkeeping, created = MonthlyBookkeeping.objects.update_or_create(
            user=request.user,
            month=first_day,
            defaults={
                'total_revenue': Decimal(str(data.get('total_revenue', 0))),
                'vat_amount': Decimal(str(data.get('vat_amount', 0))),
                'gross_salary': Decimal(str(data.get('gross_salary', 0))),
                'vacation_pay': Decimal(str(data.get('vacation_pay', 0))),
                'pension': Decimal(str(data.get('pension', 0))),
                'sick_pay': Decimal(str(data.get('sick_pay', 0))),
                'overheads': Decimal(str(data.get('overheads', 0))),
                'social_contributions': Decimal(str(data.get('social_contributions', 0))),
                'profit': Decimal(str(data.get('profit', 0))),
            }
        )

        return JsonResponse({'status': 'success', 'message': f'Bookkeeping saved for {month_str}.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
