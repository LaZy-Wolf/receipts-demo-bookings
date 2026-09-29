from datetime import datetime, timedelta, timezone


def weekly(start_local: datetime, end_local: datetime, count: int) -> list[tuple[datetime, datetime]]:
    """`count` weekly occurrences of [start_local, end_local), returned as UTC pairs.

    `start_local` and `end_local` are aware datetimes in the room's time zone.
    """
    # Add weeks on the local wall clock, then convert: a 09:00 meeting stays at 09:00 after DST changes.
    return [
        ((start_local + timedelta(weeks=i)).astimezone(timezone.utc),
         (end_local + timedelta(weeks=i)).astimezone(timezone.utc))
        for i in range(count)
    ]
