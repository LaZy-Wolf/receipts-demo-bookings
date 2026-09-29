from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass
class Room:
    id: int
    name: str
    timezone: str
    capacity: int
    hourly_rate_cents: int
    peak_rate_cents: int

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    @classmethod
    def from_row(cls, row) -> "Room":
        return cls(**{k: row[k] for k in row.keys()})


@dataclass
class Booking:
    id: int
    room_id: int
    series_id: str | None
    title: str
    organizer: str
    start: datetime  # aware, UTC
    end: datetime  # aware, UTC
    price_cents: int
    status: str
    fee_cents: int | None

    @classmethod
    def from_row(cls, row) -> "Booking":
        data = {k: row[k] for k in row.keys()}
        data["start"] = datetime.fromisoformat(data.pop("start_utc"))
        data["end"] = datetime.fromisoformat(data.pop("end_utc"))
        return cls(**data)
