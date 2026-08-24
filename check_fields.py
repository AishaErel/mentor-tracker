"""
Prints the EXACT field names for a specific table, straight from Airtable's
schema — no guessing, no typos. Use this whenever you get an
UNKNOWN_FIELD_NAME error.

Run with: python check_fields.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_id = os.getenv("AIRTABLE_BASE_ID")
token = os.getenv("AIRTABLE_TOKEN")

url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
data = response.json()

if response.status_code != 200:
    print("Error:", data)
else:
    for table in data.get("tables", []):
        print(f"\n=== TABLE: '{table['name']}' ===")
        for field in table.get("fields", []):
            print(f"  '{field['name']}'   (type: {field['type']})")