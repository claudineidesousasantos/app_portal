from django import template

register = template.Library()

@register.filter
def filter_by_day(working_hours, day):
    return working_hours.filter(day_of_week=day)
