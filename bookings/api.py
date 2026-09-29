import sqlite3
import uuid
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import Blueprint, Response, abort, current_app, jsonify, make_response, request

from . import ical
from .cancellation import cancellation_fee
from .db import get_db
from .models import Booking, Room
from .overlap import first_conflict
from .pricing import price_cents
from .recurrence import weekly

bp = Blueprint("api", __name__)


def error(status: int, message: str):
    return jsonify({"error": message}), status


def load_room(room_id: int) -> Room:
    row = get_db().execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
    if row is None:
        abort(404)
    return Room.from_row(row)


def load_booking(booking_id: int) -> Booking:
    row = get_db().execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if row is None:
        abort(404)
    return Booking.from_row(row)


def active_bookings(room_id: int) -> list[Booking]:
    rows = get_db().execute(
        "SELECT * FROM bookings WHERE room_id = ? AND status = 'active' ORDER BY start_utc", (room_id,)
    ).fetchall()
    return [Booking.from_row(r) for r in rows]


def room_json(room: Room) -> dict:
    return {"id": room.id, "name": room.name, "timezone": room.timezone, "capacity": room.capacity,
            "hourly_rate_cents": room.hourly_rate_cents, "peak_rate_cents": room.peak_rate_cents}


def booking_json(b: Booking, room: Room) -> dict:
    return {"id": b.id, "room_id": b.room_id, "series_id": b.series_id, "title": b.title, "organizer": b.organizer,
            "start": b.start.isoformat(), "end": b.end.isoformat(), "price_cents": b.price_cents,
            "status": b.status, "fee_cents": b.fee_cents}


def parse_local(value, room: Room) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        abort(make_response(error(400, f"invalid datetime: {value!r}")))
    if dt.tzinfo is not None:
        return dt.astimezone(room.tz)
    return dt.replace(tzinfo=room.tz)


@bp.get("/rooms")
def list_rooms():
    rows = get_db().execute("SELECT * FROM rooms ORDER BY name").fetchall()
    return jsonify([room_json(Room.from_row(r)) for r in rows])


@bp.post("/rooms")
def create_room():
    data = request.get_json(force=True)
    try:
        ZoneInfo(data["timezone"])
        name = data["name"]
    except (KeyError, ValueError, ZoneInfoNotFoundError):
        return error(400, "name and a valid IANA timezone are required")
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO rooms (name, timezone, capacity, hourly_rate_cents, peak_rate_cents) VALUES (?, ?, ?, ?, ?)",
            (name, data["timezone"], int(data.get("capacity", 4)), int(data.get("hourly_rate_cents", 0)),
             int(data.get("peak_rate_cents", data.get("hourly_rate_cents", 0)))),
        )
    except sqlite3.IntegrityError:
        return error(409, "room name already exists")
    db.commit()
    return jsonify(room_json(load_room(cur.lastrowid))), 201


@bp.get("/rooms/<int:room_id>/bookings")
def room_bookings(room_id: int):
    room = load_room(room_id)
    bookings = active_bookings(room_id)
    if "date" in request.args:
        day = date.fromisoformat(request.args["date"])
        bookings = [b for b in bookings if b.start.astimezone(room.tz).date() == day]
    return jsonify([booking_json(b, room) for b in bookings])


@bp.post("/rooms/<int:room_id>/bookings")
def create_booking(room_id: int):
    room = load_room(room_id)
    data = request.get_json(force=True)
    for field in ("title", "organizer", "start", "end"):
        if not data.get(field):
            return error(400, f"{field} is required")
    start_local = parse_local(data["start"], room)
    end_local = parse_local(data["end"], room)
    count = int(data.get("repeat_weekly", 1))
    if not 1 <= count <= 52:
        return error(400, "repeat_weekly must be between 1 and 52")

    occurrences = weekly(start_local, end_local, count)
    existing = active_bookings(room_id)
    for start, end in occurrences:
        clash = first_conflict(start, end, existing)
        if clash is not None:
            return error(409, f"overlaps booking {clash.id} ({clash.title})")

    db = get_db()
    series_id = uuid.uuid4().hex if count > 1 else None
    ids = []
    for start, end in occurrences:
        price = price_cents(room, start.astimezone(room.tz), end.astimezone(room.tz))
        cur = db.execute(
            "INSERT INTO bookings (room_id, series_id, title, organizer, start_utc, end_utc, price_cents) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (room_id, series_id, data["title"], data["organizer"], start.isoformat(), end.isoformat(), price),
        )
        ids.append(cur.lastrowid)
    db.commit()
    created = [booking_json(load_booking(i), room) for i in ids]
    return jsonify(created[0] if count == 1 else created), 201


@bp.get("/bookings/<int:booking_id>")
def get_booking(booking_id: int):
    booking = load_booking(booking_id)
    return jsonify(booking_json(booking, load_room(booking.room_id)))


@bp.post("/bookings/<int:booking_id>/cancel")
def cancel_booking(booking_id: int):
    booking = load_booking(booking_id)
    if booking.status != "active":
        return error(409, "booking is not active")
    now = current_app.config["CLOCK"]()
    if booking.start <= now:
        return error(409, "booking has already started")
    fee = cancellation_fee(booking.price_cents, booking.start, now)
    db = get_db()
    db.execute("UPDATE bookings SET status = 'cancelled', fee_cents = ? WHERE id = ?", (fee, booking_id))
    db.commit()
    return jsonify(booking_json(load_booking(booking_id), load_room(booking.room_id)))


@bp.get("/rooms/<int:room_id>/calendar.ics")
def room_calendar(room_id: int):
    room = load_room(room_id)
    now = current_app.config["CLOCK"]()
    upcoming = [b for b in active_bookings(room_id) if b.end > now - timedelta(days=1)]
    return Response(ical.calendar(room, upcoming, now), mimetype="text/calendar")
