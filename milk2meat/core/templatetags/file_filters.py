from django import template

register = template.Library()


@register.filter
def split(value, separator):
    """
    Split a string on the given separator and return a list of parts.
    Usage: {{ value|split:"/" }}
    """
    return value.split(separator)
