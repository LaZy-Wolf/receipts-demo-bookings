from datetime import datetime, timezone


def escape(text: str) -> str:
    return text


def _stamp(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def calendar(room, bookings, now: datetime) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//receipts-demo//bookings//EN",
             f"X-WR-CALNAME:{escape(room.name)}"]
    for b in bookings:
        lines += [
            "BEGIN:VEVENT",
            f"UID:booking-{b.id}@bookings.example",
            f"DTSTAMP:{_stamp(now)}",
            f"DTSTART:{_stamp(b.start)}",
            f"DTEND:{_stamp(b.end)}",
            f"SUMMARY:{escape(b.title)}",
            f"ORGANIZER;CN={escape(b.organizer)}:mailto:{b.organizer}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
