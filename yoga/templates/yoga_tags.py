from django import template

register = template.Library()

@register.filter
def get_complexity_class(value):
    if value == 1:
        return "bg-success"
    elif value == 2:
        return "bg-warning text-dark"
    elif value == 3:
        return "bg-danger"
    return "bg-secondary"

