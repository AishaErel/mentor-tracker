"""
Coordinator-facing AI agent.

Two capabilities:
1. generate_weekly_summary() — reads this week's mentor check-ins and produces
   a categorized brief (Urgent / Attendance / Progress / Logistics) instead of
   the coordinator reading every raw submission themselves.
2. send_reminder_emails() — finds mentors who haven't submitted this week and
   emails them a reminder, using Gmail SMTP.

Both are intentionally simple starting points. Natural next steps:
- Compare this week's summary to prior weeks to surface trends, not just a snapshot
- Let the coordinator ask follow-up questions about the summary (multi-turn, not one-shot)
- Track reminder open/response rates
"""

import os
import smtplib
from email.mime.text import MIMEText
from anthropic import Anthropic

from mentor_checkins import get_checkins_for_week, get_missing_checkins
from mentors import get_all_mentors

client = Anthropic()
MODEL = "claude-sonnet-5"

SUMMARY_SYSTEM_PROMPT = """You are an assistant helping a program coordinator quickly
understand this week's mentor check-ins for a youth mentorship program.

You will receive a list of this week's check-in submissions. Produce a concise,
categorized summary using these exact section headers as markdown:

### Urgent
Anything flagged by a mentor or requiring immediate attention. If nothing, write "Nothing urgent this week."

### Attendance
Brief note on overall attendance patterns and any groups with notable absences.

### Progress
Brief note on discussion topics, activities, and any patterns worth knowing.

### Logistics
Food confirmations, coordinator meeting attendance, or other operational notes worth flagging.

Keep each section to 2-3 sentences maximum. Be specific (mention counts, group
names, or details from the data) rather than generic. This is a working summary
for someone who will act on it today, not a report for later reading."""


def generate_weekly_summary(week_of: str) -> str:
    """
    Pulls this week's check-ins and asks Claude to produce a categorized brief.
    Returns markdown text ready to render with st.markdown().
    """
    checkins = get_checkins_for_week(week_of)

    if not checkins:
        return "### No check-ins submitted yet this week."

    lines = []
    for record in checkins:
        f = record["fields"]
        lines.append(
            f"- Group: {f.get('Group Name (from Mentor)', 'Unknown')} | "
            f"Food confirmed: {f.get('Food Confirmed')} | "
            f"Students expected: {f.get('Students Expected')} | "
            f"Not coming: {f.get('Students Not Coming', '')} | "
            f"Reasons: {f.get('Reasons', '')} | "
            f"Attended coordinator meeting: {f.get('Attended Coord Meeting')} | "
            f"Discussion topic: {f.get('Discussion Topic of the Week', '')} | "
            f"Activity: {f.get('Activity Name of the Week', '')} | "
            f"Mentor's flag: {f.get('Flagged Situation', '')} | "
            f"AI flag: {f.get('AI Flag Reason', '')} | "
            f"Notes: {f.get('Notes To Coordinator', '')}"
        )

    data_text = "\n".join(lines)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=SUMMARY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"This week's check-ins:\n\n{data_text}"}],
        )
        return response.content[0].text
    except Exception as e:
        return f"Summary generation failed: {e}"


def send_reminder_emails(week_of: str) -> dict:
    """
    Finds mentors who haven't submitted a check-in for the given week and
    emails each one a reminder.

    Requires SENDER_EMAIL and SENDER_APP_PASSWORD in .env (a Gmail address
    with an App Password, not your regular password — generate one at
    https://myaccount.google.com/apppasswords).

    Returns: {"sent_to": [names], "failed": [names], "already_submitted": count}
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_APP_PASSWORD")

    if not sender_email or not sender_password:
        return {"error": "SENDER_EMAIL / SENDER_APP_PASSWORD not set in .env"}

    all_mentors = get_all_mentors()
    all_mentor_ids = [m["id"] for m in all_mentors]
    mentor_by_id = {m["id"]: m["fields"] for m in all_mentors}

    missing_ids = get_missing_checkins(all_mentor_ids, week_of)

    sent_to = []
    failed = []

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        for mentor_id in missing_ids:
            mentor = mentor_by_id.get(mentor_id, {})
            name = mentor.get("Name", "Mentor")
            email = mentor.get("Email")

            if not email:
                failed.append(name)
                continue

            body = (
                f"Hi {name},\n\n"
                f"Just a friendly reminder to submit your weekly check-in for the week of {week_of}.\n\n"
                f"Thank you!"
            )
            msg = MIMEText(body)
            msg["Subject"] = "Weekly check-in reminder"
            msg["From"] = sender_email
            msg["To"] = email

            try:
                server.sendmail(sender_email, email, msg.as_string())
                sent_to.append(name)
            except Exception:
                failed.append(name)

        server.quit()
    except Exception as e:
        return {"error": f"Could not connect to email server: {e}"}

    return {
        "sent_to": sent_to,
        "failed": failed,
        "already_submitted": len(all_mentor_ids) - len(missing_ids),
    }