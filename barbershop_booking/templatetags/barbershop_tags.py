from django import template

register = template.Library()

@register.filter
def filter_by_day(working_hours, day):
    if not working_hours or not isinstance(working_hours, dict):
        return []
    return working_hours.get(day, [])

