CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    timezone TEXT NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 4,
    hourly_rate_cents INTEGER NOT NULL DEFAULT 0,
    peak_rate_cents INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    series_id TEXT,
    title TEXT NOT NULL,
    organizer TEXT NOT NULL,
    start_utc TEXT NOT NULL,
    end_utc TEXT NOT NULL,
    price_cents INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    fee_cents INTEGER
);

CREATE INDEX IF NOT EXISTS bookings_room ON bookings(room_id, start_utc);
