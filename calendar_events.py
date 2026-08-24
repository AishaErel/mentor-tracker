"""
Functions specific to the AcademicCalendar table.
"""

import os
from airtable_client import list_records, create_record

TABLE_NAME = os.getenv("AIRTABLE_CALENDAR_TABLE", "AcademicCalendar")


def add_event(event_name: str, event_date: str, event_time: str = "",event_location: str = "", group_name: str = "", description: str = "") -> dict:
    """
    event_date: "YYYY-MM-DD"
    event_time: formatted string like "6:30 PM" (optional)
    event_location: formatted string (optional)
    """
    fields = {
        "Event Name": event_name,
        "Date": event_date,
        "Time": event_time,
        "Location": event_location,
        "Group Name": group_name,    # blank = applies to everyone
        "Description": description,
    }
    return create_record(TABLE_NAME, fields)


def get_all_events() -> list[dict]:
    """All events, sorted by date ascending."""
    records = list_records(TABLE_NAME)
    return sorted(records, key=lambda r: r["fields"].get("Date", ""))


def get_general_events() -> list[dict]:
    """Only events with no specific group set — i.e. events that apply to everyone."""
    records = list_records(TABLE_NAME, formula="{Group Name} = ''")
    return sorted(records, key=lambda r: r["fields"].get("Date", ""))


def get_upcoming_events(from_date: str) -> list[dict]:
    """Events on or after from_date (YYYY-MM-DD), sorted by Airtable's default order."""
    return list_records(TABLE_NAME, formula=f"IS_AFTER({{Date}}, '{from_date}')")


def get_events_for_group(group_name: str) -> list[dict]:
    """Events for a specific group, plus events with no group set (applies to all)."""
    formula = f"OR({{Group Name}} = '{group_name}', {{Group Name}} = '')"
    return list_records(TABLE_NAME, formula=formula)