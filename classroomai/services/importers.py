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


def parse_course_from_text(text: str) -> Dict:
    """Parse a free-form OCR text into a course dict (best-effort).
    Heuristics:
    - Prefer labeled lines like: 課程名稱/Title, 教師/Instructor, 教室/Location/Classroom, 說明/Description
    - Fallback: first non-empty line as title; the rest become description.
    """
    import re

    lines = [ln.strip() for ln in (text or "").splitlines()]
    lines = [ln for ln in lines if ln]

    title = ""
    instructor = ""
    classroom = ""
    desc_parts: List[str] = []

    patterns = [
        ("title", re.compile(r"^(課程名稱|課程|title|course)\s*[:：]\s*(.+)$", re.I)),
        ("instructor", re.compile(r"^(教師|老師|instructor|teacher)\s*[:：]\s*(.+)$", re.I)),
        ("classroom", re.compile(r"^(教室|地點|location|classroom)\s*[:：]\s*(.+)$", re.I)),
        ("description", re.compile(r"^(說明|描述|description)\s*[:：]\s*(.+)$", re.I)),
    ]

    consumed = set()
    for idx, ln in enumerate(lines):
        for key, pat in patterns:
            m = pat.match(ln)
            if m:
                val = m.group(2).strip()
                if key == "title" and not title:
                    title = val
                    consumed.add(idx)
                elif key == "instructor" and not instructor:
                    instructor = val
                    consumed.add(idx)
                elif key == "classroom" and not classroom:
                    classroom = val
                    consumed.add(idx)
                elif key == "description":
                    desc_parts.append(val)
                    consumed.add(idx)
                break

    # Fallbacks
    if not title and lines:
        title = lines[0]
        consumed.add(0)
    # Remaining lines become description
    for idx, ln in enumerate(lines):
        if idx not in consumed:
            desc_parts.append(ln)

    description = "\n".join(desc_parts).strip()
    return {
        "title": title[:255],
        "description": description,
        "instructor": instructor[:100],
        "classroom": classroom[:100],
    }


