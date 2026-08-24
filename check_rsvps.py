"""
Prints every RSVP record raw, plus every upcoming AcademicCalendar event's ID,
so we can compare them side by side and catch a mismatch.

Run with: python check_rsvps.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_id = os.getenv("AIRTABLE_BASE_ID")
token = os.getenv("AIRTABLE_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

rsvps_table = os.getenv("AIRTABLE_RSVPS_TABLE", "EventRSVPs")
calendar_table = os.getenv("AIRTABLE_CALENDAR_TABLE", "AcademicCalendar")


def get_records(table_name):
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    response = requests.get(url, headers=headers)
    return response.json().get("records", [])


print("=== AcademicCalendar records (id + name) ===")
for r in get_records(calendar_table):
    print(f"  id={r['id']}   Event Name={r['fields'].get('Event Name')}")

print("\n=== EventRSVPs raw records ===")
for r in get_records(rsvps_table):
    print(f"  id={r['id']}")
    print(f"    fields={r['fields']}")