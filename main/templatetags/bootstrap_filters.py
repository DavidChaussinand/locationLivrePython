# main/templatetags/bootstrap_filters.py
from django import template

register = template.Library()

@register.filter(name='attr')
def add_attr(field, css):
    attrs = {}
    definition = css.split(',')
    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            t, v = d.split(':')
            attrs[t] = v
    return field.as_widget(attrs=attrs)
