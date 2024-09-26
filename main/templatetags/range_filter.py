# main/templatetags/range_filter.py
from django import template

register = template.Library()

@register.filter(name='range')
def make_range(start, end):
    return range(start, end)
