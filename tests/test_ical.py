from datetime import datetime, timezone

from bookings.ical import calendar
from bookings.models import Booking, Room

ROOM = Room(1, "Fjord", "Europe/Oslo", 4, 0, 0)
NOW = datetime(2026, 3, 2, 12, 0, tzinfo=timezone.utc)


def booking(title="Planning"):
    return Booking(7, 1, None, title, "ana@example.com", datetime(2026, 3, 3, 8, 0, tzinfo=timezone.utc),
                   datetime(2026, 3, 3, 9, 0, tzinfo=timezone.utc), 0, "active", None)


def test_structure():
    ics = calendar(ROOM, [booking()], NOW)
    assert ics.startswith("BEGIN:VCALENDAR\r\n")
    assert ics.endswith("END:VCALENDAR\r\n")
    assert "DTSTART:20260303T080000Z\r\n" in ics
    assert "SUMMARY:Planning\r\n" in ics


def test_uid_is_stable():
    assert "UID:booking-7@bookings.example" in calendar(ROOM, [booking()], NOW)
