"""Small, testable helpers for weekly navigation, Persian formatting and dates.

Kept separate from views so the date math can be unit-tested without HTTP.
The Jalali conversion is a compact, dependency-free implementation so the
project does not need an extra package just to display Persian dates.
"""
from __future__ import annotations

from datetime import date, timedelta

from .models import Day

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

PERSIAN_MONTHS = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
]


def to_persian_digits(value) -> str:
    """Convert ASCII digits in ``value`` to Persian digits."""
    return str(value).translate(PERSIAN_DIGITS)


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    """Convert a Gregorian date to the Jalali (Solar Hijri) calendar."""
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    gy2 = gy + 1 if gm > 2 else gy
    days = (
        355666
        + (365 * gy)
        + ((gy2 + 3) // 4)
        - ((gy2 + 99) // 100)
        + ((gy2 + 399) // 400)
        + gd
        + sum(g_days_in_month[: gm - 1])
    )

    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365

    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)

    return jy, jm, jd


def format_jalali(value: date, *, with_year: bool = False) -> str:
    """Format a Gregorian date as a Persian string, e.g. ``۲۸ شهریور``."""
    jy, jm, jd = gregorian_to_jalali(value.year, value.month, value.day)
    text = f"{jd} {PERSIAN_MONTHS[jm - 1]}"
    if with_year:
        text = f"{text} {jy}"
    return to_persian_digits(text)


def start_of_week(value: date) -> date:
    """Return the Saturday that begins the week containing ``value``."""
    offset = Day.from_python_weekday(value.weekday())
    return value - timedelta(days=offset)


def parse_week_param(raw: str | None, *, today: date | None = None) -> date:
    """Normalize a ``?week=YYYY-MM-DD`` value to the week's Saturday.

    Any date inside the week is accepted; invalid input falls back to the
    current week. Returns the Saturday start date.
    """
    today = today or date.today()
    if raw:
        try:
            return start_of_week(date.fromisoformat(raw))
        except ValueError:
            pass
    return start_of_week(today)


def week_days(week_start: date) -> list[dict]:
    """Build the ordered list of Persian day descriptors for a week."""
    today = date.today()
    names = Day.persian_names()
    short_names = Day.short_persian_names()
    days = []
    for index in range(7):
        current = week_start + timedelta(days=index)
        value = Day.from_python_weekday(current.weekday())
        days.append(
            {
                "value": value,
                "name": names[value],
                "short_name": short_names[value],
                "date": current,
                "date_fa": format_jalali(current),
                "date_fa_full": format_jalali(current, with_year=True),
                "is_today": current == today,
            }
        )
    return days


def week_range_label(week_start: date) -> str:
    """Persian label for a week, e.g. ``۲۸ شهریور تا ۳ مهر``."""
    week_end = week_start + timedelta(days=6)
    return f"{format_jalali(week_start)} تا {format_jalali(week_end)}"
