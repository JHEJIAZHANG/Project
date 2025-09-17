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


def parse_multiple_courses_from_timetable(text: str) -> List[Dict]:
    """Enhanced parser for weekly timetable OCR text to multiple course dicts.
    
    Handles both horizontal and vertical timetable formats.
    Strategy:
    1. Detect time patterns and course information
    2. Parse day-of-week markers
    3. Extract course names, times, and locations
    4. Group by course and create schedule entries
    """
    import re
    from datetime import datetime
    
    txt = (text or '').replace('\r', '\n').strip()
    if not txt:
        return []
    
    courses = []
    lines = [ln.strip() for ln in txt.split('\n') if ln.strip()]
    
    # Enhanced patterns for Chinese timetables
    day_patterns = {
        '週一': 0, '星期一': 0, '一': 0, 'Monday': 0,
        '週二': 1, '星期二': 1, '二': 1, 'Tuesday': 1,
        '週三': 2, '星期三': 2, '三': 2, 'Wednesday': 2,
        '週四': 3, '星期四': 3, '四': 3, 'Thursday': 3,
        '週五': 4, '星期五': 4, '五': 4, 'Friday': 4,
        '週六': 5, '星期六': 5, '六': 5, 'Saturday': 5,
        '週日': 6, '星期日': 6, '日': 6, 'Sunday': 6,
    }
    
    # Time patterns (HH:MM-HH:MM, HH:MM HH:MM, etc.)
    time_pattern = re.compile(r'(\d{1,2}:\d{2})\s*[-~—至到]\s*(\d{1,2}:\d{2})')
    single_time_pattern = re.compile(r'(\d{1,2}:\d{2})')
    
    # Course name patterns (Chinese characters + alphanumeric)
    course_name_pattern = re.compile(r'[\u4e00-\u9fa5][\u4e00-\u9fa5A-Za-z0-9\s\-\(\)]{2,30}')
    
    # Classroom patterns
    classroom_patterns = [
        re.compile(r'(電\d{3}[^(]*\([^)]+\))', re.I),  # 電708(承曦樓)
        re.compile(r'(電\d{3})', re.I),  # 電101, 電203
        re.compile(r'(\d{3}教室)', re.I),  # 101教室
        re.compile(r'(教\d{3})', re.I),  # 教101
        re.compile(r'(實驗室\d*)', re.I),  # 實驗室, 實驗室1
        re.compile(r'(\d{3})', re.I),  # 101, 203
        re.compile(r'(教室)', re.I),  # 教室
    ]
    
    # Instructor patterns
    instructor_pattern = re.compile(r'([^\s]{2,4}[P]?)\s*$')  # 蔡文隆P, 許晉龍
    
    # Check if this is a vertical timetable format (like the test image)
    has_vertical_format = any('節次' in line or '第一節' in line for line in lines)
    
    if has_vertical_format:
        return _parse_vertical_timetable(lines, day_patterns, time_pattern, 
                                       course_name_pattern, classroom_patterns, 
                                       instructor_pattern)
    else:
        return _parse_horizontal_timetable(lines, day_patterns, time_pattern, 
                                         course_name_pattern, classroom_patterns, 
                                         instructor_pattern)


def _parse_vertical_timetable(lines, day_patterns, time_pattern, course_name_pattern, 
                            classroom_patterns, instructor_pattern):
    """Parse vertical timetable format where courses are listed in columns."""
    import re
    
    courses = []
    current_courses = {}  # title -> course_data
    
    # Enhanced course name pattern for better Chinese recognition
    enhanced_course_pattern = re.compile(r'[\u4e00-\u9fa5]{2,20}(?:應用|設計|實務|專題|安全|倫理|法律|管理|智慧|人工|多媒體|電腦|資訊)')
    
    # Enhanced instructor pattern
    enhanced_instructor_pattern = re.compile(r'([\u4e00-\u9fa5]{2,4}[P]?)\s*$')
    
    # Enhanced classroom pattern
    enhanced_classroom_pattern = re.compile(r'(電\d{3}[^(]*\([^)]+\)|藝\d{3}|教\d{3}|實驗室\d*|\d{3}教室)')
    
    # Find day markers and course information
    current_day = -1
    course_blocks = []
    
    # Process lines to find course blocks
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for day markers
        for day_str, day_num in day_patterns.items():
            if day_str in line:
                current_day = day_num
                break
        
        # Look for course information blocks
        if current_day != -1 and line:
            # Check if this line contains course information
            if (enhanced_course_pattern.search(line) or 
                enhanced_instructor_pattern.search(line) or 
                enhanced_classroom_pattern.search(line)):
                
                # Collect course information in this block
                course_info = []
                j = i
                while (j < len(lines) and 
                       lines[j].strip() and 
                       not any(day_str in lines[j] for day_str in day_patterns.keys()) and
                       not lines[j].strip().startswith('第') and  # Skip period markers
                       not re.match(r'^\d{1,2}:\d{2}$', lines[j].strip())):  # Skip time markers
                    if lines[j].strip():
                        course_info.append(lines[j].strip())
                    j += 1
                
                if course_info:
                    course_blocks.append((current_day, course_info))
                i = j - 1  # Skip processed lines
        
        i += 1
    
    # Process course blocks with improved logic
    for day, course_info in course_blocks:
        # Extract course name, instructor, and classroom
        course_name = ""
        instructor = ""
        classroom = ""
        
        # Process each piece of information
        for info in course_info:
            info = info.strip()
            if not info:
                continue
                
            # Check for course name (usually longer Chinese text)
            if not course_name and enhanced_course_pattern.search(info):
                course_name = enhanced_course_pattern.search(info).group(0).strip()
            
            # Check for instructor (usually 2-4 Chinese characters with optional P)
            elif not instructor and enhanced_instructor_pattern.search(info):
                instructor = enhanced_instructor_pattern.search(info).group(1).strip()
            
            # Check for classroom (usually contains numbers and specific keywords)
            elif not classroom and enhanced_classroom_pattern.search(info):
                classroom = enhanced_classroom_pattern.search(info).group(1).strip()
        
        # Only create course if we have a valid course name
        if course_name and len(course_name) >= 2:
            # Clean up course name (remove extra characters)
            course_name = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9\s\-\(\)]', '', course_name).strip()
            
            # Clean up instructor
            if instructor:
                instructor = re.sub(r'[^\u4e00-\u9fa5A-Za-z]', '', instructor).strip()
            
            # Clean up classroom
            if classroom:
                classroom = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9\(\)]', '', classroom).strip()
            
            # Create or update course
            if course_name not in current_courses:
                current_courses[course_name] = {
                    'title': course_name,
                    'description': '',
                    'instructor': instructor,
                    'classroom': classroom,
                    'schedule': []
                }
            
            # Add schedule entry
            schedule_entry = {
                'dayOfWeek': day,
                'startTime': '08:10',  # Default start time
                'endTime': '17:10'     # Default end time
            }
            current_courses[course_name]['schedule'].append(schedule_entry)
    
    # Convert to list and filter out invalid courses
    for course_data in current_courses.values():
        if (course_data['schedule'] and 
            course_data['title'] and 
            len(course_data['title']) >= 2):
            courses.append({
                'title': course_data['title'][:255],
                'description': course_data['description'][:1000],
                'instructor': course_data['instructor'][:100],
                'classroom': course_data['classroom'][:100],
                'schedule': course_data['schedule']
            })
    
    return courses[:15]


def _parse_horizontal_timetable(lines, day_patterns, time_pattern, course_name_pattern, 
                              classroom_patterns, instructor_pattern):
    """Parse horizontal timetable format (original logic)."""
    courses = []
    current_courses = {}  # title -> course_data
    current_day = -1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for day markers
        for day_str, day_num in day_patterns.items():
            if day_str in line:
                current_day = day_num
                line = re.sub(rf'^{re.escape(day_str)}\s*', '', line).strip()
                break
        
        if current_day == -1:
            continue
        
        # Look for time patterns
        time_match = time_pattern.search(line)
        if time_match:
            start_time, end_time = time_match.groups()
            course_text = line[time_match.end():].strip()
            
            course_name = ""
            course_match = course_name_pattern.search(course_text)
            if course_match:
                course_name = course_match.group(0).strip()
            
            if course_name:
                classroom = ""
                for pattern in classroom_patterns:
                    classroom_match = pattern.search(course_text)
                    if classroom_match:
                        classroom = classroom_match.group(0)
                        break
                
                instructor = ""
                instructor_match = instructor_pattern.search(course_text)
                if instructor_match:
                    instructor = instructor_match.group(1)
                
                if course_name not in current_courses:
                    current_courses[course_name] = {
                        'title': course_name,
                        'description': '',
                        'instructor': instructor,
                        'classroom': classroom,
                        'schedule': []
                    }
                
                schedule_entry = {
                    'dayOfWeek': current_day,
                    'startTime': start_time,
                    'endTime': end_time
                }
                current_courses[course_name]['schedule'].append(schedule_entry)
    
    # Convert to list
    for course_data in current_courses.values():
        if course_data['schedule']:
            courses.append({
                'title': course_data['title'][:255],
                'description': course_data['description'][:1000],
                'instructor': course_data['instructor'][:100],
                'classroom': course_data['classroom'][:100],
                'schedule': course_data['schedule']
            })
    
    return courses[:15]


