from django import template

register = template.Library()

@register.filter
def format_duration(duration):
    if not duration:
        return ""

    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if hours > 0:
        parts.append(f'{hours}h')
    if minutes > 0:
        parts.append(f'{minutes}m')
    if seconds > 0 or not parts:
        parts.append(f'{seconds}s')

    return "".join(parts)
