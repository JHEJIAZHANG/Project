import csv
import io
from typing import List, Dict


def parse_courses_csv(data: bytes, encoding: str = "utf-8") -> List[Dict]:
    """Parse CSV bytes to course dicts.

    Expected headers (case-insensitive, optional):
    - title (required)
    - description
    - instructor
    - classroom
    """
    text = data.decode(encoding, errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    out: List[Dict] = []
    for row in reader:
        if not row:
            continue
        title = (row.get("title") or row.get("Title") or row.get("課程名稱") or "").strip()
        if not title:
            continue
        out.append({
            "title": title,
            "description": (row.get("description") or row.get("Description") or row.get("說明") or "").strip(),
            "instructor": (row.get("instructor") or row.get("Instructor") or row.get("教師") or "").strip(),
            "classroom": (row.get("classroom") or row.get("Classroom") or row.get("教室") or "").strip(),
        })
    return out


def parse_courses_ical(data: bytes) -> List[Dict]:
    """Parse iCalendar bytes to course dicts using VEVENT summary/description/location.
    We only extract basic metadata for course creation.
    """
    from icalendar import Calendar

    cal = Calendar.from_ical(data)
    out: List[Dict] = []
    for component in cal.walk():
        if component.name != "VEVENT":
            continue
        title = str(component.get("SUMMARY", "")).strip()
        if not title:
            continue
        desc = str(component.get("DESCRIPTION", "")).strip()
        loc = str(component.get("LOCATION", "")).strip()
        out.append({
            "title": title,
            "description": desc,
            "instructor": "",
            "classroom": loc,
        })
    return out


