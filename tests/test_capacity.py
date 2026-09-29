def test_too_many_attendees(room, book):
    r = room(capacity=4)
    assert book(r, "2026-03-10T09:00", "2026-03-10T10:00", attendees=5).status_code == 400


def test_attendees_within_capacity(room, book):
    r = room(capacity=4)
    assert book(r, "2026-03-10T09:00", "2026-03-10T10:00", attendees=4).status_code == 201
