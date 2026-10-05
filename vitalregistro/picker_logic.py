"""Calendar and wheel arithmetic without a GUI dependency."""
import calendar
from datetime import date


def wheel_index(scroll_y, count):
    return max(0, min(count - 1, int((1 - scroll_y) * (count - 1) + .5)))


def wheel_position(index, count):
    return 1 if count <= 1 else 1 - index / (count - 1)


def valid_date(year, month, day):
    return date(year, month, min(max(1, day), calendar.monthrange(year, month)[1]))


def format_day(value):
    """strftime %Y is not zero-padded for years <1000 on every platform."""
    return f"{value.day:02}/{value.month:02}/{value.year:04}"
