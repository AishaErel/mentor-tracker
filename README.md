# High School Girls Tracker

A weekly check-in and coordination system built for a youth mentorship program, where 10 mentors run weekly sessions for approximately 40 high school students across multiple grade cohorts.

**Live demo:** [deployed Streamlit link]
*(The live demo runs on a separate Airtable base with fictional data — no real student or mentor information is public.)*

---

## Why I built this

I'm a high school coordinator responsible for 10 mentors and around 40 students, split across grade-level groups that meet weekly. Before this project, tracking attendance, weekly plans, student progress, and urgent situations meant chasing information across text messages, spreadsheets, and memory — with no easy way to see, at a glance, who had checked in, who needed follow-up, or what was happening across the whole program in a given week.

I built this system to solve that directly: a lightweight, structured, and private way for mentors and students to check in weekly, for me to track attendance and flag situations that need attention, and for the whole program's information — event calendars, RSVPs, mentor plans — to live in one place instead of scattered across tools.

## What it does

- **Mentor check-ins** — weekly attendance, food logistics, discussion topics, and a space to flag anything urgent
- **Student check-ins** — attendance, prayer and memorization goals, reading progress, and activity requests, submitted via group + nickname (no accounts needed, and real names stay private from other students)
- **Events calendar** — general program events with an RSVP flow for students
- **Coordinator dashboard** — password-protected view showing flagged situations, attendance gaps, and upcoming events at a glance
- **AI safety-net layer** — an independent AI pass over mentors' free-text notes to catch wellbeing concerns that might not be explicitly flagged, running alongside (not instead of) manual flagging
- **AI weekly summary** — an on-demand, categorized brief (Urgent / Attendance / Progress / Logistics) generated from that week's real check-in data, so I don't have to read every submission manually
- **Parent-facing group updates** — a privacy-conscious view showing only group-level discussion topics and activities, never individual student data

## Tech stack

- **Frontend:** Streamlit (Python)
- **Data:** Airtable, accessed via its REST API — chosen for fast iteration on the data model (linked records, lookups) without standing up a full database
- **AI:** Anthropic's Claude API (Claude Haiku for lightweight concern detection, Claude Sonnet for weekly summary generation)
- **Auth:** lightweight password gate for the coordinator view; group + nickname flow for students (no account system needed at this scale)

## Project structure

```
app.py                    — main Streamlit app, all UI and page logic
airtable_client.py        — shared Airtable auth + generic get/create/update/delete
mentors.py                — Mentors table logic
mentor_checkins.py        — WeeklyCheckins table logic (submissions, flags)
students.py               — Students table logic (group/nickname lookups)
student_checkins.py       — StudentsCheckins table logic
calendar_events.py        — AcademicCalendar table logic
rsvps.py                  — EventRSVPs table logic
ai_layer.py                — AI concern-detection safety net
coordinator_agent.py      — AI weekly summary generation
assets/                   — logo and avatar SVGs
```

## Setup

1. Clone this repo and open it in your editor of choice.
2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your own values:
   - **Airtable**: create a base with the tables listed above (see field names in each `*.py` file's docstring), then generate a Personal Access Token (Airtable → Developer Hub) scoped to that base with `data.records:read`, `data.records:write`, and `schema.bases:read`.
   - **Anthropic**: get an API key at [console.anthropic.com](https://console.anthropic.com).
   - Set a coordinator password and your name for the dashboard greeting.
4. Run it:
   ```
   streamlit run app.py
   ```

## Deploying your own demo

This project is designed so a public deployment never touches real user data:

1. Duplicate your Airtable base and replace real names/events with fictional placeholders.
2. Get a separate API token scoped only to that demo base.
3. Push this repo to GitHub (`.env` is git-ignored — never committed).
4. Deploy on [Streamlit Community Cloud](https://share.streamlit.io), connecting your GitHub repo.
5. Add your demo credentials in the deployed app's **Settings → Secrets** panel (not in the repo).

## This is a work in progress..

This is still a work in progress, which I am planning to be updating and imroving regularly. 
