from datetime import datetime


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """True if the two time ranges share any time."""
    # Ranges are half-open [start, end): touching ends do not overlap.
    return a_start < b_end and b_start < a_end


def first_conflict(start: datetime, end: datetime, existing) -> object | None:
    for other in existing:
        if overlaps(start, end, other.start, other.end):
            return other
    return None
