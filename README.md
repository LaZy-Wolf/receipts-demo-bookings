# bookings

Meeting-room booking API for our offices in several time zones.

- Flask 3, SQLite through the standard `sqlite3` module
- Each room has a time zone. Clients send and receive **local times of the room**; storage is UTC.
- Money is integer cents

## Running

```bash
pip install -e ".[test]"
flask --app bookings run
pytest
```

## API

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/rooms` | |
| POST | `/rooms` | `{"name", "timezone", "capacity", "hourly_rate_cents", "peak_rate_cents"}` |
| GET | `/rooms/<id>/bookings?date=YYYY-MM-DD` | Bookings on that local date |
| POST | `/rooms/<id>/bookings` | `{"title", "organizer", "start", "end", "repeat_weekly": n}`. `start`/`end` are room-local, e.g. `"2026-03-23T09:00"`. |
| GET | `/bookings/<id>` | Times are returned in the room's time zone, with offset |
| POST | `/bookings/<id>/cancel` | Returns the cancellation fee |
| GET | `/rooms/<id>/calendar.ics` | iCalendar (RFC 5545) feed of upcoming bookings |

### Rules

- Bookings in the same room may not overlap. Back-to-back bookings (one ends at 10:00, the next starts at 10:00) are fine.
- A booking must end after it starts.
- `repeat_weekly: n` creates `n` weekly occurrences at the same **local** time, also across daylight-saving changes.
- Price: `hourly_rate_cents` per hour, but minutes between 17:00 and 19:00 local time are charged at `peak_rate_cents`.
- Cancelling less than 24 hours before the start costs 50% of the price. Earlier cancellations are free.
