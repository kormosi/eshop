from django import template
from django.template.defaultfilters import floatformat

register = template.Library()


@register.filter
def sk_price(value, decimal_places=2):
    """Format a number with a comma decimal separator, e.g. 18.90 -> 18,90."""
    return floatformat(value, decimal_places).replace(".", ",")
