from datetime import datetime, time, timedelta


def period_bounds(days, today=None):
    """Calendar days inclusive, ending at the end of today."""
    today = today or datetime.now().date()
    if days is None:
        return None, None
    return (datetime.combine(today - timedelta(days=days - 1), time.min),
            datetime.combine(today, time(23, 59)))
