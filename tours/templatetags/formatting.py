from django import template
from decimal import Decimal, ROUND_HALF_UP
from datetime import date as _date, datetime as _datetime
from django.utils import timezone

register = template.Library()


def _to_int(value):
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    try:
        return int(round(float(value)))
    except Exception:
        # Fallback: try string cleanup then int
        try:
            return int(str(value).split('.')[0])
        except Exception:
            return 0


@register.filter(name="vn_intcomma")
def vn_intcomma(value):
    """
    Format number using Vietnamese thousands separator '.' with no decimals.
    Examples:
    1000 -> '1.000'
    1234567 -> '1.234.567'
    """
    amount = _to_int(value)
    formatted = f"{amount:,}".replace(",", ".")
    return formatted


def _to_datetime(value):
    if value is None or value == "":
        return None
    if isinstance(value, _datetime):
        return value if timezone.is_aware(value) else timezone.make_aware(value, timezone.get_current_timezone())
    if isinstance(value, _date):
        # Treat date as midnight local time
        return _datetime(value.year, value.month, value.day, tzinfo=timezone.get_current_timezone())
    # Try common string/timestamp inputs without being too strict
    try:
        if isinstance(value, (int, float)):
            return _datetime.fromtimestamp(float(value), tz=timezone.get_current_timezone())
        if isinstance(value, str):
            v = value.strip()
            # Try ISO first
            try:
                dt = _datetime.fromisoformat(v)
                return dt if timezone.is_aware(dt) else timezone.make_aware(dt, timezone.get_current_timezone())
            except Exception:
                pass
            # Try common formats
            for fmt in [
                "%Y-%m-%d %H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%d/%m/%Y",
            ]:
                try:
                    dt = _datetime.strptime(v, fmt)
                    if fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                        # No time part: treat as local midnight
                        dt = _datetime(dt.year, dt.month, dt.day, tzinfo=timezone.get_current_timezone())
                    else:
                        dt = dt if timezone.is_aware(dt) else timezone.make_aware(dt, timezone.get_current_timezone())
                    return dt
                except Exception:
                    continue
    except Exception:
        return None
    return None


@register.filter(name="vn_date")
def vn_date(value):
    """Safely format a date/datetime/parsable string to 'dd/mm/YYYY'.
    - None/empty -> 'Chưa xác định'
    - Handles date, datetime (naive/aware), ISO strings, and common formats.
    - Converts to local timezone.
    """
    dt = _to_datetime(value)
    if not dt:
        return "Chưa xác định"
    try:
        dt_local = timezone.localtime(dt)
        return dt_local.strftime("%d/%m/%Y")
    except Exception:
        return "Chưa xác định"


@register.filter(name="vn_datetime")
def vn_datetime(value):
    """Safely format a datetime/parsable string to 'dd/mm/YYYY HH:MM'.
    - None/empty -> 'Chưa xác định'
    - Handles datetime (naive/aware), ISO strings, and common formats.
    - Converts to local timezone.
    """
    dt = _to_datetime(value)
    if not dt:
        return "Chưa xác định"
    try:
        dt_local = timezone.localtime(dt)
        return dt_local.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return "Chưa xác định"


@register.filter(name="subtract")
def subtract(value, arg):
    """
    Subtract arg from value. Returns the result as a number.
    Usage: {{ booking.total_price|subtract:booking.deposit_amount }}
    """
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (ValueError, TypeError, decimal.InvalidOperation):
        return 0
