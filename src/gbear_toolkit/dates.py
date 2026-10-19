from datetime import datetime, timedelta, timezone


def to_iso(date_str: str) -> str:
    """Convert M/D/YYYY (e.g. '6/22/2026') to ISO format (YYYY-MM-DD)."""
    return datetime.strptime(date_str, "%m/%d/%Y").date().isoformat()
