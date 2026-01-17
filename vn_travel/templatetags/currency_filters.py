from django import template

register = template.Library()

def format_vn_number(value):
    """
    Helper function to format numbers with Vietnamese dot separator.
    Examples:
        1000000 -> 1.000.000
        1750000 -> 1.750.000
    """
    if value is None:
        return "0"
    
    try:
        # Convert to int to remove decimal places
        int_value = int(float(value))
        # Format with dot separator (Vietnamese style)
        formatted = "{:,}".format(int_value).replace(',', '.')
        return formatted
    except (ValueError, TypeError):
        return str(value)

@register.filter(name='currency')
def currency(value):
    """
    Format a number as Vietnamese currency (integer only, no decimals).
    Examples:
        1000000 -> 1.000.000
        1750000.00 -> 1.750.000
    """
    return format_vn_number(value)

@register.filter(name='currency_vnd')
def currency_vnd(value):
    """
    Format a number as Vietnamese currency with VND suffix.
    Examples:
        1000000 -> 1.000.000 VND
        1750000.00 -> 1.750.000 VND
    """
    formatted = format_vn_number(value)
    return f"{formatted} VND"

@register.filter(name='vn_intcomma')
def vn_intcomma(value):
    """
    Format a number with Vietnamese dot separator (alias for currency).
    Examples:
        1000000 -> 1.000.000
        1750000.00 -> 1.750.000
    """
    return format_vn_number(value)
