from datetime import datetime, timedelta, timezone

# Datetimes:
#   aware - carries a tzinfo, e.g. datetime(2024, 3, 5, 9, 0, tzinfo=timezone.utc)
#   naive - no tzinfo, e.g. datetime(2024, 3, 5, 9, 0); Python can't tell which zone it's in
# Zones are fixed UTC offsets, e.g. tz_offset(-5). They don't follow DST;
# only to_local / now_local track DST, using the computer's own zone settings.


def print_iso_tz(days: int = 7, hours: int = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days, hours=hours)
    return dt.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


# -----------------------------------------------------------------------------
# Zones

def tz_offset(hours: int, minutes: int = 0) -> timezone:
    # Fixed-offset zone, e.g. tz_offset(-5) -> UTC-05:00, tz_offset(5, 30) -> UTC+05:30
    # For negative half-hour offsets, pass both negative: tz_offset(-3, -30)
    return timezone(timedelta(hours=hours, minutes=minutes))


# -----------------------------------------------------------------------------
# Current time

def now_utc() -> datetime:
    # Aware datetime in UTC, e.g. 2024-03-05 14:00:00+00:00
    return datetime.now(timezone.utc).replace(microsecond=0)

def now_local() -> datetime:
    # Aware datetime in the computer's zone, e.g. 2024-03-05 09:00:00-05:00
    return datetime.now().astimezone().replace(microsecond=0)

def now_in(tz: timezone) -> datetime:
    # Aware datetime in a fixed zone, e.g. now_in(tz_offset(9)) -> 2024-03-05 23:00:00+09:00
    return datetime.now(tz).replace(microsecond=0)


# -----------------------------------------------------------------------------
# Checks

def is_aware(dt: datetime) -> bool:
    # True if dt carries a timezone, False if naive
    return dt.tzinfo is not None and dt.utcoffset() is not None


# -----------------------------------------------------------------------------
# Attaching, converting and removing timezones

def make_aware(dt: datetime, tz: timezone = timezone.utc) -> datetime:
    # Attaches a zone to a naive datetime without shifting the clock time:
    #   09:00 (naive) -> 09:00-05:00 with tz_offset(-5)
    if is_aware(dt):
        raise ValueError(f'Datetime already has a timezone ({dt.tzinfo}); use to_tz to convert')
    return dt.replace(tzinfo=tz)

def to_tz(dt: datetime, tz: timezone) -> datetime:
    # Converts an aware datetime to another zone; same moment, different clock time:
    #   14:00+00:00 -> 09:00-05:00 with tz_offset(-5)
    if not is_aware(dt):
        raise ValueError('Datetime is naive; use make_aware first')
    return dt.astimezone(tz)

def to_utc(dt: datetime) -> datetime:
    # Shortcut for to_tz(dt, timezone.utc)
    return to_tz(dt, timezone.utc)

def to_local(dt: datetime) -> datetime:
    # Converts to the computer's zone, DST included
    if not is_aware(dt):
        raise ValueError('Datetime is naive; use make_aware first')
    return dt.astimezone()

def make_naive(dt: datetime, tz: timezone = timezone.utc) -> datetime:
    # Converts to tz first, then drops the tzinfo (e.g. for DBs that store naive UTC)
    return to_tz(dt, tz).replace(tzinfo=None)


# -----------------------------------------------------------------------------
# Offsets

def utc_offset(dt: datetime) -> str:
    # Offset of an aware datetime as a string, e.g. 09:00-05:00 -> '-05:00'
    if not is_aware(dt):
        raise ValueError('Datetime is naive; use make_aware first')
    offset = dt.strftime('%z')  # e.g. '-0500'
    return offset[:3] + ':' + offset[3:]

def local_offset() -> str:
    # The computer's current offset, e.g. '-04:00' in New York during DST
    return utc_offset(now_local())


# -----------------------------------------------------------------------------
# Parsing and formatting

def from_iso(s: str, tz: timezone = timezone.utc) -> datetime:
    # Parses an ISO 8601 string into an aware datetime:
    #   '2024-03-05T14:00:00Z'      -> 2024-03-05 14:00:00+00:00
    #   '2024-03-05T09:00:00-05:00' -> keeps its own offset
    #   '2024-03-05 09:00'          -> no offset, so tz is attached
    dt = datetime.fromisoformat(s.strip())
    return dt if is_aware(dt) else make_aware(dt, tz)

def to_iso_utc(dt: datetime) -> str:
    # Formats as UTC with a trailing Z, e.g. '2024-03-05T14:00:00Z' (same format as print_iso_tz)
    return to_utc(dt).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')


# -----------------------------------------------------------------------------
# Unix timestamps - seconds since 1970-01-01 UTC, always zone-independent

def from_timestamp(ts: int | float, tz: timezone = timezone.utc) -> datetime:
    # e.g. 1709647200 -> 2024-03-05 14:00:00+00:00
    # Timestamps in milliseconds (13 digits) need dividing by 1000 first
    return datetime.fromtimestamp(ts, tz)

def to_timestamp(dt: datetime) -> int:
    # e.g. 2024-03-05 14:00:00+00:00 -> 1709647200
    if not is_aware(dt):
        raise ValueError('Datetime is naive; use make_aware first')
    return int(dt.timestamp())
