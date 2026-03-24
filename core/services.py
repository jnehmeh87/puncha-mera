import requests
import datetime
import logging
from django.core.cache import cache
from .models import ExchangeRate

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """
    A service class to manage currency conversions using the Frankfurter API.
    Rates are cached daily in the local database to avoid N+1 API calls and prevent rate limits.
    """
    API_BASE_URL = "https://api.frankfurter.app"

    @classmethod
    def get_rate(cls, date: datetime.date, base_currency: str, target_currency: str) -> float:
        if base_currency == target_currency:
            return 1.0

        # Optimization: Frankfurter handles dates up to today. Future dates use today's.
        today = datetime.date.today()
        if date > today:
            date = today
            
        # 1. Check local cache
        try:
            rate_obj = ExchangeRate.objects.get(date=date, base_currency=base_currency, target_currency=target_currency)
            return float(rate_obj.rate)
        except ExchangeRate.DoesNotExist:
            pass

        # 2. Check if the API is known to be down (Circuit Breaker)
        if cache.get('frankfurter_api_down'):
            return 1.0
            
        # 3. If not in cache, fetch from API
        # Frankfurter API format for historical rates: {base_url}/{date}?from={base}&to={target}
        # e.g. https://api.frankfurter.app/2021-01-01?from=USD&to=EUR
        date_str = date.strftime("%Y-%m-%d")
        url = f"{cls.API_BASE_URL}/{date_str}?from={base_currency}&to={target_currency}"

        try:
            # We use a very aggressive 1.5s timeout. If it's slower than that, we can't afford to block the web worker.
            response = requests.get(url, timeout=1.5)
            response.raise_for_status()
            data = response.json()
            
            if 'rates' in data and target_currency in data['rates']:
                rate_value = data['rates'][target_currency]
                
                # Save to cache
                ExchangeRate.objects.create(
                    date=date,
                    base_currency=base_currency,
                    target_currency=target_currency,
                    rate=rate_value
                )
                return float(rate_value)
            else:
                logger.warning(f"Frankfurter API returned unexpected format for {base_currency} to {target_currency} on {date}")
                return 1.0 # Fallback
                
        except Exception as e:
            logger.error(f"Failed to fetch exchange rate from Frankfurter API: {e}")
            # Trip the circuit breaker for 10 minutes so subsequent calls don't also hang and stall the entire Gunicorn worker pool
            cache.set('frankfurter_api_down', True, 600)
            return 1.0 # Fallback to 1:1 if API is down to not break analytics entirely
            
    @classmethod
    def convert(cls, amount: float, date: datetime.date, base_currency: str, target_currency: str) -> float:
        """Converts an amount from base currency to target currency on a specific date."""
        rate = cls.get_rate(date, base_currency, target_currency)
        return float(amount) * rate

    @classmethod
    def prefetch_rates(cls, date_range: list, currencies_from: set, currency_to: str):
        """
        Actively fetches missing rates for a given set of dates and currencies to front-load API calls.
        Useful for running right before heavy analytics aggregation.
        """
        for date in date_range:
            for c_from in currencies_from:
                if c_from != currency_to:
                    cls.get_rate(date, c_from, currency_to)
