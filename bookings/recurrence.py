from datetime import datetime, timedelta, timezone


def weekly(start_local: datetime, end_local: datetime, count: int) -> list[tuple[datetime, datetime]]:
    """`count` weekly occurrences of [start_local, end_local), returned as UTC pairs.

    `start_local` and `end_local` are aware datetimes in the room's time zone.
    """
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    return [(start_utc + timedelta(weeks=i), end_utc + timedelta(weeks=i)) for i in range(count)]
