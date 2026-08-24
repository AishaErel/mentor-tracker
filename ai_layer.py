"""
Lightweight AI safety-net layer.

Purpose: mentors sometimes mention something concerning in free-text fields
(Notes to Coordinator, Reasons, Discussion Topic) without realizing it needs
attention, or without checking the "Flagged Situation" box themselves. This
module runs a fast classification pass over that text and surfaces anything
that might need a coordinator's eyes, as a second layer on top of manual
flagging.

This is intentionally a starting point: today it does binary detection with
a short reason. Natural next steps (not yet built):
- Severity levels (low/medium/high) instead of binary
- Trend detection across a student/group's history, not just one submission
- A feedback loop where coordinators mark false positives to improve prompting
"""

import os
import json
from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY from environment

MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are a safety-review assistant for a youth mentorship program.
You will receive free-text notes a mentor wrote about their weekly session.

Decide if anything in the text suggests a student's safety, wellbeing, or
mental health might need a coordinator's attention -- even if the mentor
didn't explicitly flag it. Look for things like: signs of distress, family
or health issues, safety concerns, or anything hinting at a student
struggling, not just normal logistics (schedule conflicts, mild lateness,
ordinary absences are NOT concerns).

Respond with ONLY a JSON object, no other text, no markdown fences:
{"concern_detected": true or false, "reason": "one sentence explaining why, or empty string if no concern"}

Be conservative: only flag genuine possible wellbeing/safety signals, not
routine scheduling notes."""


def check_for_concerns(notes_to_coordinator: str, reasons: str, discussion_topic: str, flagged_situation: str = "") -> dict:
    """
    Runs a quick AI pass over a mentor's free-text submission to catch
    wellbeing/safety signals that weren't explicitly flagged.

    Returns: {"ai_flagged": bool, "ai_flag_reason": str}
    Fails safe: if the API call errors for any reason, returns no flag
    rather than blocking the mentor's submission.
    """
    combined_text = "\n".join(filter(None, [
        f"Notes to coordinator: {notes_to_coordinator}" if notes_to_coordinator else "",
        f"Reasons for absences: {reasons}" if reasons else "",
        f"Discussion topic: {discussion_topic}" if discussion_topic else "",
        f"Mentor's own urgent flag: {flagged_situation}" if flagged_situation else "",
    ]))

    if not combined_text.strip():
        return {"ai_flagged": False, "ai_flag_reason": ""}

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": combined_text}],
        )
        raw_text = response.content[0].text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1].replace("json", "", 1).strip()

        parsed = json.loads(raw_text)
        return {
            "ai_flagged": bool(parsed.get("concern_detected", False)),
            "ai_flag_reason": parsed.get("reason", ""),
        }
    except Exception as e:
        print(f"AI concern-check failed (failing safe, no flag applied): {e}")
        return {"ai_flagged": False, "ai_flag_reason": ""}