from django import template

register = template.Library()

@register.filter
def star_rating(value, i):
    if value >= i:
        return "full"
    elif value >= i - 0.5:
        return "half"
    else:
        return "empty"
