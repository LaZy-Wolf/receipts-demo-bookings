from datetime import datetime, timedelta, timezone

from bookings.cancellation import cancellation_fee

NOW = datetime(2026, 3, 2, 12, 0, tzinfo=timezone.utc)


def test_fee_inside_window():
    assert cancellation_fee(6000, NOW + timedelta(hours=2), NOW) == 3000


def test_fee_just_inside_window():
    assert cancellation_fee(6000, NOW + timedelta(hours=23, minutes=59), NOW) == 3000
