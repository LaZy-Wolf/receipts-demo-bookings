from datetime import datetime
from zoneinfo import ZoneInfo

from bookings.models import Room
from bookings.pricing import price_cents

TZ = ZoneInfo("Europe/Berlin")
ROOM = Room(1, "A", "Europe/Berlin", 4, hourly_rate_cents=3000, peak_rate_cents=4500)


def local(hour, minute=0):
    return datetime(2026, 3, 10, hour, minute, tzinfo=TZ)


def test_off_peak_hours():
    assert price_cents(ROOM, local(9), local(11)) == 6000


def test_half_hour():
    assert price_cents(ROOM, local(10), local(10, 30)) == 1500


def test_fully_in_peak():
    assert price_cents(ROOM, local(17), local(18)) == 4500
