from datetime import datetime, timezone

from bookings.overlap import overlaps


def t(hour, minute=0):
    return datetime(2026, 3, 10, hour, minute, tzinfo=timezone.utc)


def test_disjoint():
    assert not overlaps(t(9), t(10), t(11), t(12))


def test_partial_overlap():
    assert overlaps(t(9), t(11), t(10), t(12))


def test_contained():
    assert overlaps(t(9), t(12), t(10), t(11))


def test_identical():
    assert overlaps(t(9), t(10), t(9), t(10))
