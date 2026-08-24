"""
Shared Airtable connector.

Every table-specific file (mentors.py, checkins.py, calendar_events.py)
imports from here instead of re-writing auth/request logic.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

if not AIRTABLE_TOKEN or not AIRTABLE_BASE_ID:
    raise EnvironmentError(
        "Missing AIRTABLE_TOKEN or AIRTABLE_BASE_ID. "
        "Copy .env.example to .env and fill in your values."
    )

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json",
}


def _table_url(table_name: str) -> str:
    return f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}"


def list_records(table_name: str, formula: str = None, max_records: int = 100) -> list[dict]:
    """
    Fetch records from a table. Optionally filter with an Airtable formula string,
    e.g. formula="{Active} = TRUE()"
    Returns a list of dicts like: {"id": "recXXXX", "fields": {...}}
    """
    params = {"maxRecords": max_records}
    if formula:
        params["filterByFormula"] = formula

    response = requests.get(_table_url(table_name), headers=HEADERS, params=params)
    if response.status_code != 200:
        print("AIRTABLE ERROR RESPONSE:", response.json())
    response.raise_for_status()
    return response.json().get("records", [])


def create_record(table_name: str, fields: dict) -> dict:
    """Create a single record. `fields` is a dict of {column_name: value}."""
    payload = {"fields": fields}
    response = requests.post(_table_url(table_name), headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def update_record(table_name: str, record_id: str, fields: dict) -> dict:
    """Update specific fields on an existing record without touching the rest."""
    url = f"{_table_url(table_name)}/{record_id}"
    payload = {"fields": fields}
    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def delete_record(table_name: str, record_id: str) -> dict:
    url = f"{_table_url(table_name)}/{record_id}"
    response = requests.delete(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()