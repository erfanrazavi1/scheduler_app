from django import template

from ..utils import format_jalali, to_persian_digits

register = template.Library()


@register.filter(name="fa_digits")
def fa_digits(value):
    """Render ASCII digits as Persian digits, e.g. ``14:00`` -> ``۱۴:۰۰``."""
    if value is None:
        return ""
    return to_persian_digits(value)


@register.filter(name="fa_jalali")
def fa_jalali(value, with_year=False):
    """Render a date using the Jalali calendar."""
    if not value:
        return ""
    return format_jalali(value, with_year=bool(with_year))
