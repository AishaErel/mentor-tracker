"""
Compares group names across Mentors and Students tables, and shows what's
actually stored in WeeklyCheckins — helps catch mismatches like
"9th Grade" vs "9th grade" vs "9th Grade A".

Run with: python check_groups.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_id = os.getenv("AIRTABLE_BASE_ID")
token = os.getenv("AIRTABLE_TOKEN")
headers = {"Authorization": f"Bearer {token}"}


def get_records(table_name):
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    response = requests.get(url, headers=headers)
    return response.json().get("records", [])


mentors_table = os.getenv("AIRTABLE_MENTORS_TABLE", "Mentors")
students_table = os.getenv("AIRTABLE_STUDENTS_TABLE", "Students")
checkins_table = os.getenv("AIRTABLE_CHECKINS_TABLE", "WeeklyCheckins")

print("=== Group Names in MENTORS ===")
for r in get_records(mentors_table):
    print(f"  '{r['fields'].get('Group Name')}'  (mentor: {r['fields'].get('Name')})")

print("\n=== Group Names in STUDENTS ===")
seen = set()
for r in get_records(students_table):
    g = r["fields"].get("Group Name")
    if g not in seen:
        print(f"  '{g}'")
        seen.add(g)

print("\n=== WeeklyCheckins: what 'Group Name (from Mentor)' actually contains ===")
for r in get_records(checkins_table):
    f = r["fields"]
    print(f"  Week: {f.get('Week Of')}  |  Group Name (from Mentor): {f.get('Group Name (from Mentor)')}")