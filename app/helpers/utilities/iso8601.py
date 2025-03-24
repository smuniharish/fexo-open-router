from datetime import timedelta
from typing import Any

import isodate


def iso8601_to_duration(iso8601_string: str) -> int | None:
    try:
        duration = isodate.parse_duration(iso8601_string)
        return duration.total_seconds()
    except ValueError:
        return None


def seconds_to_iso8601(seconds: int) -> Any:
    try:
        duration = timedelta(seconds=seconds)
        iso_duration = isodate.duration_isoformat(duration)
        return iso_duration
    except ValueError:
        return None
