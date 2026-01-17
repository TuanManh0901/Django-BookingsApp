from django import template

register = template.Library()

@register.filter(name='currency_vnd')
def currency_vnd(value):
    """
    Format a number as Vietnamese currency.
    Example: 12950000 -> 12.950.000 VNĐ
    """
    try:
        # Convert to integer to remove decimals
        value = int(float(value))
        # Format with thousand separators (Vietnamese style uses dots)
        formatted = "{:,}".format(value).replace(',', '.')
        return f"{formatted} VNĐ"
    except (ValueError, TypeError):
        return value
