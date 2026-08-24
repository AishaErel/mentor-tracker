"""
Functions specific to the WeeklyCheckins table.

Note: the "Mentor" field is a Link to another record, so Airtable expects
a LIST of record IDs, e.g. ["recXXXXXXXX"], even though it's just one mentor.
"""

import os
from datetime import date
from airtable_client import list_records, create_record

TABLE_NAME = os.getenv("AIRTABLE_CHECKINS_TABLE", "WeeklyCheckins")


def submit_checkin(
    mentor_record_id: str,
    week_of: str,                 # "YYYY-MM-DD"
    activity_name: str,
    discussion_topic: str,
    food_confirmed: bool,
    students_expected: int,
    students_not_coming: str,     # free text, e.g. "John, Maria"
    reasons: str,
    attended_coord_meeting: bool,
    notes_to_coordinator: str,
    flagged_situation: bool,
) -> dict:
    fields = {
        "Mentor": [mentor_record_id],
        "Week Of": week_of,
        "Food Confirmed": food_confirmed,
        "Students Expected": students_expected,
        "Discussion Topic of the Week":discussion_topic,
        "Activity Name of the Week": activity_name,
        "Students Not Coming": students_not_coming,
        "Reasons": reasons,
        "Attended Coord Meeting": attended_coord_meeting,
        "Notes To Coordinator": notes_to_coordinator,
        "Flagged Situation": flagged_situation,
    }
    return create_record(TABLE_NAME, fields)


def get_checkins_for_week(week_of: str) -> list[dict]:
    """All check-ins submitted for a given week (YYYY-MM-DD)."""
    return list_records(TABLE_NAME, formula=f"{{Week Of}} = '{week_of}'")


def get_flagged_checkins() -> list[dict]:
    """Anything a mentor flagged as needing your attention."""
    return list_records(TABLE_NAME, formula="{Flagged Situation} = TRUE()")


def get_missing_checkins(all_mentor_record_ids: list[str], week_of: str) -> list[str]:
    """
    Returns mentor record IDs who have NOT submitted a check-in for the given week.
    Useful for your reminder logic.
    """
    submitted = get_checkins_for_week(week_of)
    submitted_mentor_ids = set()
    for record in submitted:
        linked = record["fields"].get("Mentor", [])
        submitted_mentor_ids.update(linked)

    return [mid for mid in all_mentor_record_ids if mid not in submitted_mentor_ids]


def this_monday() -> str:
    """Helper: returns this week's Monday as YYYY-MM-DD, a sane default for 'Week Of'."""
    today = date.today()
    monday = today.fromordinal(today.toordinal() - today.weekday())
    return monday.isoformat()