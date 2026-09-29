from datetime import datetime

FEE_WINDOW_HOURS = 24
FEE_SHARE = 0.5


def cancellation_fee(price_cents: int, start: datetime, now: datetime) -> int:
    """50% of the price when cancelling less than 24 hours before `start`, otherwise free."""
    delta = start - now
    hours_until = (delta.days * 3600 + delta.seconds) / 3600
    if hours_until < FEE_WINDOW_HOURS:
        return round(price_cents * FEE_SHARE)
    return 0
