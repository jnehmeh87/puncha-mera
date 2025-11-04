from django.utils import timezone

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                user_settings = request.user.settings
                if user_settings.timezone:
                    timezone.activate(user_settings.timezone)
                else:
                    timezone.deactivate()
            except AttributeError:
                timezone.deactivate()
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response
