"""
Functions specific to the StudentsCheckins table.

Note: "Student Name" is a Link to another record field, so it expects a LIST
of record IDs, e.g. ["recXXXXXXXX"].

"Name (from Student Name)" and "Group Name (from Student Name)" are Airtable
LOOKUP fields — they auto-populate from the linked Student record once
"Student Name" is set. Never write to them directly; they're read-only.
"""

import os
from datetime import date
from airtable_client import list_records, create_record

TABLE_NAME = os.getenv("AIRTABLE_STUDENT_CHECKINS_TABLE", "StudentsCheckins")


def submit_student_checkin(
    student_record_id: str,
    week_of: str,                  # "YYYY-MM-DD"
    coming_this_week: bool,
    reason_if_not_coming: str,
    memorization_goal: str,
    salah_goal_met: str,
    book_pages: int,
    pages_read: int,
    activity_request: str,
) -> dict:
    fields = {
        "Week Of": week_of,
        "Student Name": [student_record_id],
        "Coming This Week?": coming_this_week,
        "The Reason Why (If not Coming)": reason_if_not_coming,
        "Book Pages Read": book_pages,
        "Memorization Goal": memorization_goal,
        "Salah (Prayer) Goal": salah_goal_met,
        "Quran Pages": pages_read,
        "Activity Request": activity_request,
    }
    return create_record(TABLE_NAME, fields)


def get_checkins_for_week(week_of: str) -> list[dict]:
    return list_records(TABLE_NAME, formula=f"{{Week Of}} = '{week_of}'")


def get_not_coming_this_week(week_of: str) -> list[dict]:
    """Students who marked themselves as not coming, with their reason."""
    formula = f"AND({{Week Of}} = '{week_of}', {{Coming This Week?}} = FALSE())"
    return list_records(TABLE_NAME, formula=formula)


def this_monday() -> str:
    today = date.today()
    monday = today.fromordinal(today.toordinal() - today.weekday())
    return monday.isoformat()