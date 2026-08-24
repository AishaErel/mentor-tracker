"""
Mentor + Student tracker app.
Run with: streamlit run app.py
"""

import streamlit as st
import os
from datetime import date, datetime
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

load_dotenv()

# When deployed on Streamlit Community Cloud, credentials live in
# st.secrets (set via the app's Settings > Secrets panel) instead of a
# local .env file. This merges them into the environment so every
# os.getenv(...) call in the rest of the app works identically whether
# running locally or deployed — no other file needs to change.
try:
    for key, value in st.secrets.items():
        os.environ.setdefault(key, str(value))
except Exception:
    pass  # no secrets configured (normal for local development)

from mentors import get_all_mentors
from mentor_checkins import submit_checkin, get_flagged_checkins, get_ai_flagged_checkins, this_monday
from ai_layer import check_for_concerns
from coordinator_agent import generate_weekly_summary
from students import get_all_group_names, get_nickname_map_for_group
from student_checkins import submit_student_checkin, get_not_coming_this_week
from calendar_events import get_upcoming_events, get_general_events, add_event
from rsvps import submit_rsvp, get_coming_count_for_event, get_rsvps_for_event

st.set_page_config(page_title="High School Girls Tracker", page_icon="🌙", layout="wide")

# ---------- CUSTOM STYLING ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Fraunces', serif !important;
        font-weight: 600 !important;
        color: #2B2B2B;
    }

    /* Section labels within forms */
    .section-label {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6B8F71;
        margin: 1.1rem 0 0.3rem 0;
    }
    .section-label:first-child {
        margin-top: 0;
    }

    /* Card containers (st.container(border=True)) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border: 1px solid #E4DCC9 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(43,43,43,0.05);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        border: none;
    }
    .stButton > button[kind="primary"] {
        background-color: #6B8F71;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #587a5e;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E4DCC9;
        border-radius: 12px;
        padding: 0.8rem;
    }

    /* Signature divider */
    .crescent-divider {
        text-align: center;
        color: #C7B99C;
        font-size: 0.9rem;
        letter-spacing: 0.3em;
        margin: 0.5rem 0 1.5rem 0;
    }

    /* Orbiting sparkles around the title */
    .title-orbit-wrap {
        position: relative;
        display: inline-block;
    }
    .orbit-sparkle {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 14px;
        height: 14px;
        margin: -7px 0 0 -7px;
        transform-origin: center;
        animation-name: orbit;
        animation-timing-function: linear;
        animation-iteration-count: infinite;
    }
    @keyframes orbit {
        from { transform: rotate(0deg) translateX(var(--orbit-radius)) rotate(0deg); }
        to   { transform: rotate(360deg) translateX(var(--orbit-radius)) rotate(-360deg); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- HEADER ----------
def load_svg(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

logo_svg = load_svg("assets/logo.svg")
mentor_avatar_svg = load_svg("assets/mentor_avatar.svg")
student_avatar_svg = load_svg("assets/student_avatar.svg")

st.markdown(
    f"""
    <div style="padding: 1.5rem 0 0.3rem 0; text-align:center;">
        <div class="title-orbit-wrap">
            <span class="orbit-sparkle" style="--orbit-radius:190px; animation-duration:9s; color:#C7A552; font-size:14px;">✦</span>
            <span class="orbit-sparkle" style="--orbit-radius:190px; animation-duration:9s; animation-delay:-3s; color:#D8A7A0; font-size:12px;">✦</span>
            <span class="orbit-sparkle" style="--orbit-radius:190px; animation-duration:9s; animation-delay:-6s; color:#6B8F71; font-size:16px;">✦</span>
            <h1 style="margin-bottom:0; font-size:2.4rem;">High School Girls Tracker</h1>
        </div>
        <p style="color:#8A8371; margin-top:0.3rem; font-size:1.05rem;">Weekly check-ins, at a glance.</p>
        <div style="width:170px; margin:1rem auto 0 auto;">{logo_svg}</div>
    </div>
    <div class="crescent-divider" style="text-align:center;">✦ ⁛ ✦</div>
    """,
    unsafe_allow_html=True,
)

selected = option_menu(
    menu_title=None,
    options=["Mentor Check-in", "Student Check-in", "Events Calendar", "Coordinator Dashboard"],
    icons=["mortarboard-fill", "backpack2-fill", "calendar3", "bar-chart-line-fill"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#FDEFEF"},
        "icon": {"color": "#6B8F71", "font-size": "16px"},
        "nav-link": {
            "font-family": "Inter, sans-serif",
            "font-weight": "500",
            "font-size": "15px",
            "color": "#2B2B2B",
            "text-align": "center",
            "margin": "0px",
            "padding": "12px 18px",
        },
        "nav-link-selected": {
            "background-color": "#6B8F71",
            "color": "#FFFFFF",
        },
    },
)

# ---------- MENTOR CHECK-IN ----------
if selected == "Mentor Check-in":
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
            <div style="width:44px;">{mentor_avatar_svg}</div>
            <h2 style="margin:0;">Weekly Mentor Check-in</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    mentors = get_all_mentors()
    if not mentors:
        st.warning("No mentors found. Add mentors in Airtable first.")
    else:
        mentor_names = {
            m["fields"].get("Name", f"Unnamed mentor ({m['id'][-4:]})"): m["id"]
            for m in mentors
        }
        selected_name = st.selectbox("Your name", list(mentor_names.keys()))

        with st.form("mentor_checkin_form"):
            st.markdown('<div class="section-label">Attendance</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                week_of = st.date_input("Week of", value=date.today())
                students_expected = st.number_input("Students expected", min_value=0, step=1)
            with col2:
                food_confirmed = st.checkbox("Food confirmed")
                students_not_coming = st.text_input("Students not coming (comma-separated)")

            st.markdown('<div class="section-label">This week</div>', unsafe_allow_html=True)
            discussion_topic = st.text_input("Discussion topic")
            activity_name = st.text_input("Activity name")
            reasons = st.text_area("Absent students and reasons (if known)")

            st.markdown('<div class="section-label">Your check-in</div>', unsafe_allow_html=True)
            attended_coord_meeting = st.checkbox("I attended the coordinator meeting")
            checked_meeting_notes = st.checkbox("I reviewed the meeting notes and to-do list for this week")
            flagged_situation = st.text_area("Anything urgent to flag?")
            notes_to_coordinator = st.text_area("Notes to coordinator")

            submitted = st.form_submit_button("Submit check-in", type="primary")

            if submitted:
                ai_result = check_for_concerns(
                    notes_to_coordinator=notes_to_coordinator,
                    reasons=reasons,
                    discussion_topic=discussion_topic,
                    flagged_situation=flagged_situation,
                )
                submit_checkin(
                    mentor_record_id=mentor_names[selected_name],
                    week_of=week_of.isoformat(),
                    food_confirmed=food_confirmed,
                    students_expected=int(students_expected),
                    students_not_coming=students_not_coming,
                    reasons=reasons,
                    attended_coord_meeting=attended_coord_meeting,
                    notes_to_coordinator=notes_to_coordinator,
                    flagged_situation=flagged_situation,
                    checked_meeting_notes=checked_meeting_notes,
                    discussion_topic=discussion_topic,
                    activity_name=activity_name,
                    ai_flagged=ai_result["ai_flagged"],
                    ai_flag_reason=ai_result["ai_flag_reason"],
                )
                st.success("Check-in submitted.")

# ---------- STUDENT CHECK-IN ----------
elif selected == "Student Check-in":
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
            <div style="width:44px;">{student_avatar_svg}</div>
            <h2 style="margin:0;">Weekly Student Check-in</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    group_names = get_all_group_names()
    if not group_names:
        st.warning("No students found. Add students in Airtable first.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            selected_group = st.selectbox("Your group", group_names)

        nickname_map = get_nickname_map_for_group(selected_group)

        if not nickname_map:
            st.info("No students with a nickname set yet in this group.")
        else:
            with col_b:
                selected_nickname = st.selectbox("Your nickname", list(nickname_map.keys()))

            with st.form("student_checkin_form"):
                st.markdown('<div class="section-label">Attendance</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    week_of = st.date_input("Week of", value=date.today(), key="student_week")
                    coming_this_week = st.checkbox("Coming this week", value=True)
                with col2:
                    reason_if_not_coming = st.text_input("If not coming, why?")

                st.markdown('<div class="section-label">Progress</div>', unsafe_allow_html=True)
                salah_goal_met = st.text_area("Salah (prayer) goal — how did it go this week?")
                memorization_goal = st.text_input("Memorization goal")
                col3, col4 = st.columns(2)
                with col3:
                    book_pages_read = st.number_input("Book pages read", min_value=0, step=1)
                with col4:
                    pages_read = st.number_input("Quran pages read", min_value=0, step=1)

                st.markdown('<div class="section-label">Looking ahead</div>', unsafe_allow_html=True)
                activity_request = st.text_area("Activity request for upcoming weeks")

                submitted = st.form_submit_button("Submit check-in", type="primary")

                if submitted:
                    submit_student_checkin(
                        student_record_id=nickname_map[selected_nickname],
                        week_of=week_of.isoformat(),
                        coming_this_week=coming_this_week,
                        reason_if_not_coming=reason_if_not_coming,
                        memorization_goal=memorization_goal,
                        salah_goal_met=salah_goal_met,
                        book_pages=int(book_pages_read),
                        pages_read=int(pages_read),
                        activity_request=activity_request,
                    )
                    st.success("Check-in submitted.")

# ---------- ACADEMIC CALENDAR ----------
elif selected == "Events Calendar":
    st.subheader("Events Calendar")
    st.caption("General program events — visible to everyone.")

    general_events = get_general_events()

    if general_events:
        for record in general_events:
            f = record["fields"]
            event_date_str = f.get("Date", "")
            event_time_str = f.get("Time", "")
            event_location_str = f.get("Location", "")

            display_date = event_date_str
            try:
                parsed = datetime.fromisoformat(event_date_str)
                display_date = parsed.strftime("%b %d, %Y")
            except (ValueError, AttributeError):
                pass

            with st.container(border=True):
                col_date, col_info = st.columns([1, 3])
                with col_date:
                    st.markdown(f"**{display_date}**")
                    if event_time_str:
                        st.caption(event_time_str)
                    if event_location_str:
                        st.caption(event_location_str)
                with col_info:
                    st.markdown(f"**{f.get('Event Name', 'Untitled event')}**")
                    if f.get("Description"):
                        st.write(f.get("Description"))

                    if st.session_state.get("coordinator_authenticated"):
                        coming_count = get_coming_count_for_event(record["id"])
                        st.caption(f"{coming_count} coming so far")

                    with st.expander("RSVP to this event"):
                        success_key = f"rsvp_success_{record['id']}"
                        if st.session_state.get(success_key):
                            st.success(st.session_state[success_key])
                            del st.session_state[success_key]

                        rsvp_group_names = get_all_group_names()
                        if not rsvp_group_names:
                            st.info("No students found yet.")
                        else:
                            rsvp_group = st.selectbox(
                                "Your group", rsvp_group_names, key=f"rsvp_group_{record['id']}"
                            )
                            rsvp_nickname_map = get_nickname_map_for_group(rsvp_group)

                            if not rsvp_nickname_map:
                                st.info("No students with a nickname set yet in this group.")
                            else:
                                rsvp_nickname = st.selectbox(
                                    "Your nickname",
                                    list(rsvp_nickname_map.keys()),
                                    key=f"rsvp_nickname_{record['id']}",
                                )
                                if st.button("I'm coming", key=f"rsvp_button_{record['id']}"):
                                    submit_rsvp(
                                        event_record_id=record["id"],
                                        student_record_id=rsvp_nickname_map[rsvp_nickname],
                                        coming=True,
                                    )
                                    st.session_state[success_key] = f"Successfully registered for the event, {rsvp_nickname}."
                                    st.rerun()
    else:
        st.info("No events yet.")

    st.divider()

    with st.expander("Add a new event (coordinator only)"):
        if st.session_state.get("coordinator_authenticated"):
            with st.form("add_event_form"):
                new_event_name = st.text_input("Event name")
                col_d, col_t = st.columns(2)
                with col_d:
                    new_event_date = st.date_input("Date", value=date.today())
                with col_t:
                    new_event_time = st.time_input("Time")
                new_event_description = st.text_area("Description (optional)")

                add_submitted = st.form_submit_button("Add event", type="primary")

                if add_submitted:
                    add_event(
                        event_name=new_event_name,
                        event_date=new_event_date.isoformat(),
                        event_time=new_event_time.strftime("%I:%M %p"),
                        group_name="",  # general calendar only for now
                        description=new_event_description,
                    )
                    st.success("Event added.")
                    st.rerun()
        else:
            add_password = st.text_input("Enter coordinator password to add events", type="password", key="calendar_pw")
            if st.button("Unlock", key="calendar_unlock"):
                if add_password == os.getenv("COORDINATOR_PASSWORD"):
                    st.session_state.coordinator_authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")

# ---------- COORDINATOR DASHBOARD ----------
elif selected == "Coordinator Dashboard":
    if "coordinator_authenticated" not in st.session_state:
        st.session_state.coordinator_authenticated = False

    if not st.session_state.coordinator_authenticated:
        st.subheader("Coordinator Access")
        entered_password = st.text_input("Enter coordinator password", type="password")
        if st.button("Unlock"):
            if entered_password == os.getenv("COORDINATOR_PASSWORD"):
                st.session_state.coordinator_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()

    coordinator_name = os.getenv("COORDINATOR_NAME", "Coordinator")
    st.subheader(f"Welcome back, {coordinator_name}")

    with st.container(border=True):
        st.markdown("#### This week, at a glance")

        if st.button("Generate weekly summary", type="primary"):
            with st.spinner("Reading through this week's check-ins..."):
                summary = generate_weekly_summary(this_monday())
                st.session_state["weekly_summary"] = summary

        if "weekly_summary" in st.session_state:
            st.markdown(st.session_state["weekly_summary"])

    st.divider()

    st.subheader("Coordinator Dashboard")

    flagged = get_flagged_checkins()
    ai_flagged = get_ai_flagged_checkins()
    not_coming = get_not_coming_this_week(this_monday())
    events = get_upcoming_events(this_monday())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Flagged situations", len(flagged))
    col2.metric("AI-detected concerns", len(ai_flagged))
    col3.metric("Not coming this week", len(not_coming))
    col4.metric("Upcoming events", len(events))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("### Flagged mentor situations")
        st.caption("Manually flagged by the mentor.")
        if flagged:
            for record in flagged:
                f = record["fields"]
                with st.container(border=True):
                    st.markdown(f"**Week of {f.get('Week Of')}**")
                    st.write(f.get("Flagged Situation", "No details"))
        else:
            st.info("Nothing flagged right now.")

        st.markdown("### AI-detected concerns")
        st.caption("Automatically surfaced from check-in notes — review and confirm.")
        if ai_flagged:
            for record in ai_flagged:
                f = record["fields"]
                with st.container(border=True):
                    st.markdown(f"**Week of {f.get('Week Of')}**")
                    st.write(f.get("AI Flag Reason", "No details"))
        else:
            st.info("No AI-detected concerns right now.")

        st.markdown("### Students not coming")
        st.caption("Shown with real names, since this view is for you as coordinator.")
        if not_coming:
            for record in not_coming:
                f = record["fields"]
                name = f.get("Name (from Student Name)", ["Unknown"])
                name = name[0] if isinstance(name, list) else name
                reason = f.get("The Reason Why (If not Coming)", "No reason given")
                with st.container(border=True):
                    st.markdown(f"**{name}**")
                    st.write(reason)
        else:
            st.info("Everyone's coming (or no submissions yet).")

    with right:
        st.markdown("### Upcoming events")
        if events:
            for record in events:
                f = record["fields"]
                with st.container(border=True):
                    st.markdown(f"**{f.get('Event Name')}**")
                    st.caption(f"{f.get('Date')} · {f.get('Group Name') or 'All groups'}")

                    rsvps = get_rsvps_for_event(record["id"])
                    coming_names = []
                    for r in rsvps:
                        if r["fields"].get("Coming"):
                            name = r["fields"].get("Name (from Student Name)", ["Unknown"])
                            name = name[0] if isinstance(name, list) else name
                            coming_names.append(name)

                    if coming_names:
                        st.markdown(f"**Coming ({len(coming_names)}):**")
                        st.write(", ".join(coming_names))
                    else:
                        st.caption("No RSVPs yet.")
        else:
            st.info("No upcoming events found.")