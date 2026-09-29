from datetime import datetime
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")


def instant(value):
    return datetime.fromisoformat(value)


def test_create_room(client, room):
    created = room(name="Fjord", timezone="Europe/Oslo")
    assert created["timezone"] == "Europe/Oslo"
    assert [r["name"] for r in client.get("/rooms").get_json()] == ["Fjord"]


def test_bad_timezone(client):
    assert client.post("/rooms", json={"name": "X", "timezone": "Mars/Base"}).status_code == 400


def test_create_booking_stores_local_time(room, book):
    r = room()
    resp = book(r, "2026-03-10T09:00", "2026-03-10T10:00")
    assert resp.status_code == 201
    body = resp.get_json()
    assert instant(body["start"]) == datetime(2026, 3, 10, 9, 0, tzinfo=BERLIN)
    assert body["price_cents"] == 3000


def test_overlap_rejected(room, book):
    r = room()
    book(r, "2026-03-10T09:00", "2026-03-10T10:00")
    assert book(r, "2026-03-10T09:30", "2026-03-10T10:30").status_code == 409


def test_other_room_does_not_clash(room, book):
    a, b = room(), room()
    book(a, "2026-03-10T09:00", "2026-03-10T10:00")
    assert book(b, "2026-03-10T09:00", "2026-03-10T10:00").status_code == 201


def test_missing_title(room, book):
    assert book(room(), "2026-03-10T09:00", "2026-03-10T10:00", title="").status_code == 400


def test_weekly_series(room, book):
    r = room()
    created = book(r, "2026-03-10T09:00", "2026-03-10T10:00", repeat_weekly=3).get_json()
    assert len(created) == 3
    assert len({b["series_id"] for b in created}) == 1
    assert instant(created[2]["start"]) - instant(created[0]["start"]) == (
        datetime(2026, 3, 24, 9, tzinfo=BERLIN) - datetime(2026, 3, 10, 9, tzinfo=BERLIN))


def test_bookings_by_date(client, room, book):
    r = room()
    book(r, "2026-03-10T09:00", "2026-03-10T10:00")
    book(r, "2026-03-11T09:00", "2026-03-11T10:00")
    found = client.get(f"/rooms/{r['id']}/bookings", query_string={"date": "2026-03-11"}).get_json()
    assert len(found) == 1


def test_cancel_inside_fee_window(client, clock, room, book):
    r = room()
    booking = book(r, "2026-03-10T09:00", "2026-03-10T11:00").get_json()
    clock.set(instant(booking["start"]) - (datetime(2026, 1, 1, 3) - datetime(2026, 1, 1, 0)))
    body = client.post(f"/bookings/{booking['id']}/cancel").get_json()
    assert body["status"] == "cancelled"
    assert body["fee_cents"] == 3000


def test_cancel_started_booking(client, clock, room, book):
    r = room()
    booking = book(r, "2026-03-10T09:00", "2026-03-10T11:00").get_json()
    clock.set(instant(booking["start"]))
    assert client.post(f"/bookings/{booking['id']}/cancel").status_code == 409


def test_cancelled_slot_can_be_rebooked(client, room, book):
    r = room()
    first = book(r, "2026-03-10T09:00", "2026-03-10T10:00").get_json()
    client.post(f"/bookings/{first['id']}/cancel")
    assert book(r, "2026-03-10T09:00", "2026-03-10T10:00").status_code == 201


def test_calendar_feed(client, room, book):
    r = room()
    book(r, "2026-03-10T09:00", "2026-03-10T10:00", title="Planning")
    resp = client.get(f"/rooms/{r['id']}/calendar.ics")
    assert resp.mimetype == "text/calendar"
    assert "SUMMARY:Planning" in resp.get_data(as_text=True)


def test_unknown_booking(client):
    assert client.get("/bookings/999").status_code == 404
