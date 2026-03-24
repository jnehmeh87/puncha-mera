from django import template
from accounts.models import UserProfile, Settings

register = template.Library()

@register.simple_tag(takes_context=True)
def get_profile_completion_percentage(context):
    user = context['request'].user
    if not user.is_authenticated:
        return 0

    user_profile, _ = UserProfile.objects.get_or_create(user=user)
    settings, _ = Settings.objects.get_or_create(user=user)

    profile_fields = [
        'first_name', 'last_name',
        'bio', 'profile_picture', 'address', 'country', 'county_region', 'postal_code'
    ]
    user_fields = ['first_name', 'last_name', 'email']
    settings_fields = ['currency', 'timezone', 'language', 'color_theme']

    total_fields = len(profile_fields) + len(settings_fields)
    completed_fields = 0

    for field in user_fields:
        if hasattr(user, field) and getattr(user, field):
            completed_fields += 1
    
    for field in profile_fields:
        if field not in user_fields:
            if hasattr(user_profile, field) and getattr(user_profile, field):
                completed_fields += 1
    
    for field in settings_fields:
        if hasattr(settings, field) and getattr(settings, field):
            completed_fields += 1

    if total_fields == 0:
        return 100

    completion_percentage = (completed_fields / total_fields) * 100
    return int(completion_percentage)

@register.simple_tag
def get_top_currencies():
    from accounts.forms import TOP_CURRENCIES
    return TOP_CURRENCIES

@register.simple_tag
def get_user_profile_img(user):
    try:
        if hasattr(user, 'userprofile') and user.userprofile and user.userprofile.profile_picture:
            return user.userprofile.profile_picture.url
    except Exception:
        pass
    return None