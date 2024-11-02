# core/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item_quantity(dictionary, key):
    item = dictionary.get(str(key))
    if isinstance(item, dict):
        return item.get('cantidad', 0)
    return item or 0

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0