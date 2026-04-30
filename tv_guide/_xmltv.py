"""XMLTV time-string parsing helper, shared between epg.py and admin.py."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone


def parse_xmltv_time(s: str) -> datetime:
    s = s.strip()
    match = re.match(r"(\d{14})\s*([+-]\d{4})", s)
    if match:
        dt_str, tz_str = match.groups()
        dt = datetime.strptime(dt_str, "%Y%m%d%H%M%S")
        tz_hours = int(tz_str[:3])
        tz_mins = int(tz_str[0] + tz_str[3:])
        tz = timezone(timedelta(hours=tz_hours, minutes=tz_mins))
        return dt.replace(tzinfo=tz)
    return datetime.strptime(s[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
