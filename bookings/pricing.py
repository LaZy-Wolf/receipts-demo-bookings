from datetime import datetime, time

PEAK_START = time(17, 0)
PEAK_END = time(19, 0)


def _touches_peak(start_local: datetime, end_local: datetime) -> bool:
    day = start_local.date()
    peak_start = datetime.combine(day, PEAK_START, start_local.tzinfo)
    peak_end = datetime.combine(day, PEAK_END, start_local.tzinfo)
    return start_local < peak_end and peak_start < end_local


def price_cents(room, start_local: datetime, end_local: datetime) -> int:
    """Price of a booking given in the room's local time."""
    minutes = (end_local - start_local).total_seconds() / 60
    rate = room.peak_rate_cents if _touches_peak(start_local, end_local) else room.hourly_rate_cents
    return round(rate * minutes / 60)
