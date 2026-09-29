from datetime import datetime, time

PEAK_START = time(17, 0)
PEAK_END = time(19, 0)


def _touches_peak(start_local: datetime, end_local: datetime) -> bool:
    day = start_local.date()
    peak_start = datetime.combine(day, PEAK_START, start_local.tzinfo)
    peak_end = datetime.combine(day, PEAK_END, start_local.tzinfo)
    return start_local < peak_end and peak_start < end_local


def price_cents(room, start_local: datetime, end_local: datetime) -> int:
    """Price of a booking given in the room's local time, hour by hour."""
    total = 0
    for hour in range(start_local.hour, end_local.hour):
        in_peak = PEAK_START.hour <= hour < PEAK_END.hour
        total += room.peak_rate_cents if in_peak else room.hourly_rate_cents
    return total
