"""
Functions specific to the EventRSVPs table.

Note: "Event" and "Student Name" are both Link to another record fields,
so each expects a LIST of record IDs, e.g. ["recXXXXXXXX"].
"""

import os
from airtable_client import list_records, create_record

TABLE_NAME = os.getenv("AIRTABLE_RSVPS_TABLE", "EventRSVPs")


def submit_rsvp(event_record_id: str, student_record_id: str, coming: bool) -> dict:
    fields = {
        "Event": [event_record_id],
        "Student Name": [student_record_id],
        "Coming": coming,
    }
    return create_record(TABLE_NAME, fields)


def get_rsvps_for_event(event_record_id: str) -> list[dict]:
    """
    All RSVPs for a specific event.

    Note: we fetch all RSVPs and filter in Python rather than using an
    Airtable formula, because ARRAYJOIN() on a link field returns the
    linked record's DISPLAY NAME, not its record ID — so a formula
    searching for the record ID would never match.
    """
    all_rsvps = list_records(TABLE_NAME)
    return [
        r for r in all_rsvps
        if event_record_id in r["fields"].get("Event", [])
    ]


def get_coming_count_for_event(event_record_id: str) -> int:
    rsvps = get_rsvps_for_event(event_record_id)
    return sum(1 for r in rsvps if r["fields"].get("Coming"))