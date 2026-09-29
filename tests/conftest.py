from datetime import datetime, timezone

import pytest

from bookings import create_app

# Fixed "now" for every test: Monday 2026-03-02 12:00 UTC.
NOW = datetime(2026, 3, 2, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def clock():
    state = {"now": NOW}

    def now():
        return state["now"]

    now.set = lambda value: state.update(now=value)
    return now


@pytest.fixture
def app(tmp_path, clock):
    return create_app({"DATABASE": str(tmp_path / "test.sqlite3"), "CLOCK": clock, "TESTING": True})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def room(client):
    def make(**fields):
        body = {"name": f"Room {make.n}", "timezone": "Europe/Berlin", "capacity": 6,
                "hourly_rate_cents": 3000, "peak_rate_cents": 4500}
        make.n += 1
        body.update(fields)
        resp = client.post("/rooms", json=body)
        assert resp.status_code == 201, resp.get_json()
        return resp.get_json()
    make.n = 1
    return make


@pytest.fixture
def book(client):
    def make(room, start, end, **fields):
        body = {"title": "Sync", "organizer": "ana@example.com", "start": start, "end": end}
        body.update(fields)
        return client.post(f"/rooms/{room['id']}/bookings", json=body)
    return make
