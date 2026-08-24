"""
One-time diagnostic: lists every table your Airtable token can see,
and confirms the base ID is valid.

Run with: python check_access.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_id = os.getenv("AIRTABLE_BASE_ID")
token = os.getenv("AIRTABLE_TOKEN")

print("Base ID from .env:", base_id)
print("Token starts with:", token[:12] if token else "MISSING")
print()

url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)
print()

data = response.json()

if response.status_code == 200:
    print("Tables this token can see:")
    for table in data.get("tables", []):
        print(f"  - '{table['name']}'  (id: {table['id']})")
else:
    print("Error response:", data)