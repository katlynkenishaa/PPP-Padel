import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta

st.set_page_config(page_title="draft request menu PPP", page_icon="🎾")

st.title("🎾 draft request menu PPP")

# --- PRICING DATA & LOGIC ---
WEEKDAY_RATES = [
    {"Time Slot": "06:00 – 07:00", "Price / Court / Hour": "Rp150,000", "Category": "Non-Peak"},
    {"Time Slot": "07:00 – 16:00", "Price / Court / Hour": "Rp210,000", "Category": "Morning"},
    {"Time Slot": "16:00 – 22:00", "Price / Court / Hour": "Rp249,000", "Category": "Peak"},
    {"Time Slot": "22:00 – 00:00", "Price / Court / Hour": "Rp185,000", "Category": "Late Night"},
    {"Time Slot": "00:00 – 06:00", "Price / Court / Hour": "Rp0", "Category": "Special Hours"}
]

WEEKEND_RATES = [
    {"Time Slot": "06:00 – 07:00", "Price / Court / Hour": "Rp178,000", "Category": "Early Morning"},
    {"Time Slot": "07:00 – 22:00", "Price / Court / Hour": "Rp258,000", "Category": "All Day Weekend"},
    {"Time Slot": "22:00 – 00:00", "Price / Court / Hour": "Rp199,000", "Category": "Late Night"},
    {"Time Slot": "00:00 – 06:00", "Price / Court / Hour": "Rp0", "Category": "Special Hours"}
]

DRILLING_RATES_LIST = [
    {"Pax": "1 Pax", "Price / Hour": "Rp160,000", "Cost / Person / Hour": "Rp160,000"},
    {"Pax": "2 Pax", "Price / Hour": "Rp190,000", "Cost / Person / Hour": "Rp95,000"},
    {"Pax": "3 Pax", "Price / Hour": "Rp220,000", "Cost / Person / Hour": "Rp73,333"},
    {"Pax": "4 Pax", "Price / Hour": "Rp250,000", "Cost / Person / Hour": "Rp62,500"},
]

COACHING_RATES_LIST = [
    {"Pax": "1 Pax", "Randy": "Rp450,000 / pax / hr", "Brian": "Rp450,000 / pax / hr", "Eddy": "Rp350,000 / pax / hr"},
    {"Pax": "2 Pax", "Randy": "Rp275,000 / pax / hr", "Brian": "Rp275,000 / pax / hr", "Eddy": "Rp275,000 / pax / hr"},
    {"Pax": "3 Pax", "Randy": "Rp217,000 / pax / hr", "Brian": "Rp217,000 / pax / hr", "Eddy": "Rp217,000 / pax / hr"},
    {"Pax": "4 Pax", "Randy": "Rp187,500 / pax / hr", "Brian": "Rp187,500 / pax / hr", "Eddy": "Rp187,500 / pax / hr"},
]

DRILLING_MAP = {1: 160000, 2: 190000, 3: 220000, 4: 250000}

COACHING_MAP = {
    "Coach Randy": {1: 450000, 2: 275000, 3: 217000, 4: 187500},
    "Coach Brian": {1: 450000, 2: 275000, 3: 217000, 4: 187500},
    "Coach Eddy": {1: 350000, 2: 275000, 3: 217000, 4: 187500}
}

ALL_COACHES = ["Coach Randy", "Coach Brian", "Coach Eddy"]

def get_hourly_rate(booking_datetime):
    is_weekend = booking_datetime.weekday() in [5, 6]
    hour = booking_datetime.hour

    if not is_weekend:
        if 0 <= hour < 6:
            return 0, "Special Hours"
        elif 6 <= hour < 7:
            return 150000, "Non-Peak"
        elif 7 <= hour < 16:
            return 210000, "Morning"
        elif 16 <= hour < 22:
            return 249000, "Peak"
        elif 22 <= hour < 24:
            return 185000, "Late Night"
        else:
            return 0, "Closed"
    else:
        if 0 <= hour < 6:
            return 0, "Special Hours"
        elif 6 <= hour < 7:
            return 178000, "Early Morning"
        elif 7 <= hour < 22:
            return 258000, "All Day Weekend"
        elif 22 <= hour < 24:
            return 199000, "Late Night"
        else:
            return 0, "Closed"

# --- BASE RATE CARD DISPLAY ---
with st.container(border=True):
    st.markdown("📊 **View Base Pricing Rate Card**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Weekdays**")
        st.dataframe(pd.DataFrame(WEEKDAY_RATES), hide_index=True, use_container_width=True)
    with col2:
        st.markdown("**Weekend (Saturday & Sunday)**")
        st.dataframe(pd.DataFrame(WEEKEND_RATES), hide_index=True, use_container_width=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Drilling Rates**")
        st.dataframe(pd.DataFrame(DRILLING_RATES_LIST), hide_index=True, use_container_width=True)
    with col4:
        st.markdown("**Coaching Rates**")
        st.dataframe(pd.DataFrame(COACHING_RATES_LIST), hide_index=True, use_container_width=True)

# --- CALCULATOR FORM ---
st.subheader("Court Booking Fee Calculator")

# 1. Date Input
selected_date = st.date_input("Select Date", value=date.today())

# 2. Number of Courts Option
court_option = st.selectbox(
    "Number of Courts",
    options=["1 Court", "2 Courts - Same Time", "2 Courts - Diff Time"]
)

def get_end_str(start_h, dur):
    end_h = (start_h + dur) % 24
    return "00:00" if end_h == 0 else f"{end_h:02d}:00"

time_options = [f"{hour:02d}:00" for hour in range(0, 24)]
end_time_options = [f"{hour:02d}:00" for hour in range(1, 24)] + ["00:00"]

def compute_duration(start_str, end_str):
    sh = int(start_str.split(":")[0])
    eh = 24 if end_str == "00:00" else int(end_str.split(":")[0])
    dur = eh - sh
    return dur if dur > 0 else dur + 24

# Check time overlaps between Court 1 and Court 2
def check_time_overlap():
    if court_option == "2 Courts - Same Time":
        return True
    if court_option != "2 Courts - Diff Time":
        return False
    s1 = int(st.session_state.get("c1_start_time", "17:00").split(":")[0])
    d1 = st.session_state.get("c1_play_duration", 2)
    e1 = s1 + d1

    s2 = int(st.session_state.get("c2_start_time", "17:00").split(":")[0])
    d2 = st.session_state.get("c2_play_duration", 3)
    e2 = s2 + d2

    return (s1 < e2) and (s2 < e1)

is_overlapping = check_time_overlap()

court_configs = []

if court_option == "2 Courts - Same Time":
    # --- SAME TIME CONFIGURATION ---
    s_col, d_col, e_col = st.columns(3)
    
    if "c1_start_time" not in st.session_state:
        st.session_state["c1_start_time"] = "17:00"

    if "c1_play_duration" not in st.session_state:
        st.session_state["c1_play_duration"] = 2

    if "c1_end_time" not in st.session_state:
        start_h = int(st.session_state["c1_start_time"].split(":")[0])
        st.session_state["c1_end_time"] = get_end_str(start_h, st.session_state["c1_play_duration"])

    def cb_same_start():
        sh = int(st.session_state["c1_start_time"].split(":")[0])
        dur = st.session_state.get("c1_play_duration", 1)
        st.session_state["c1_end_time"] = get_end_str(sh, dur)

    def cb_same_dur():
        sh = int(st.session_state["c1_start_time"].split(":")[0])
        dur = st.session_state["c1_play_duration"]
        st.session_state["c1_end_time"] = get_end_str(sh, dur)

    def cb_same_end():
        st.session_state["c1_play_duration"] = compute_duration(
            st.session_state["c1_start_time"], 
            st.session_state["c1_end_time"]
        )

    with s_col:
        st.selectbox("Start Time", time_options, key="c1_start_time", on_change=cb_same_start)
    with d_col:
        st.selectbox("Play Duration", options=list(range(1, 25)), format_func=lambda x: f"{x} hr" if x == 1 else f"{x} hrs", key="c1_play_duration", on_change=cb_same_dur)
    with e_col:
        st.selectbox("End Time", options=end_time_options, key="c1_end_time", on_change=cb_same_end)

    def cb_same_drill():
        if st.session_state.get("c1_include_drilling"):
            st.session_state["c1_include_coaching"] = False

    def cb_same_coach():
        if st.session_state.get("c1_include_coaching"):
            st.session_state["c1_include_drilling"] = False

    # Drilling setup
    c_drilling = st.toggle("Include Drilling?", key="c1_include_drilling", disabled=st.session_state.get("c1_include_coaching", False), on_change=cb_same_drill)
    drill_court_target = "Both Courts"
    c_drill_pax = 0

    if c_drilling:
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            drill_court_target = st.radio("Apply Drilling To:", options=["Court 1 Only", "Court 2 Only", "Both Courts"], horizontal=True, key="same_drill_target")
        with d_col2:
            c_drill_pax = st.radio("Number of Pax for Drilling:", options=[1, 2, 3, 4], format_func=lambda x: f"{x} Pax", horizontal=True, key="c1_drilling_pax")

    # Coaching setup
    c_coaching = st.toggle("Include Coaching?", key="c1_include_coaching", disabled=st.session_state.get("c1_include_drilling", False), on_change=cb_same_coach)
    coach_court_target = "Both Courts"
    coaching_assignments = {}

    if c_coaching:
        coach_court_target = st.radio("Apply Coaching To:", options=["Court 1 Only", "Court 2 Only", "Both Courts"], horizontal=True, key="same_coach_target")

        if coach_court_target == "Court 1 Only":
            c1_col1, c1_col2 = st.columns(2)
            with c1_col1:
                c1_coach = st.selectbox("Select Coach (Court 1):", options=ALL_COACHES, key="same_c1_coach_only")
            with c1_col2:
                c1_pax = st.radio("Number of Pax for Coaching (Court 1):", options=[1, 2, 3, 4], format_func=lambda x: f"{x} Pax", horizontal=True, key="same_c1_pax_only")
            coaching_assignments[1] = {"coach_name": c1_coach, "pax": c1_pax}

        elif coach_court_target == "Court 2 Only":
            c2_col1, c2_col2 = st.columns(2)
            with c2_col1:
                c2_coach = st.selectbox("Select Coach (Court 2):", options=ALL_COACHES, key="same_c2_coach_only")
            with c2_col2:
                c2_pax = st.radio("Number of Pax for Coaching (Court 2):", options=[1, 2, 3, 4], format_func=lambda x: f"{x} Pax", horizontal=True, key="same_c2_pax_only")
            coaching_assignments[2] = {"coach_name": c2_coach, "pax": c2_pax}

        else: # Both Courts
            st.markdown("**Court 1 Coaching**")
            c1_col1, c1_col2 = st.columns(2)
            with c1_col1:
                c1_coach = st.selectbox("Select Coach (Court 1):", options=ALL_COACHES, key="same_c1_coach")
            with c1_col2:
                c1_pax = st.radio("Number of Pax for Coaching (Court 1):", options=[1, 2, 3, 4], format_func=lambda x: f"{x} Pax", horizontal=True, key="same_c1_pax")

            avail_c2 = [c for c in ALL_COACHES if c != c1_coach]
            if st.session_state.get("same_c2_coach") not in avail_c2:
                st.session_state["same_c2_coach"] = avail_c2[0]

            st.markdown("**Court 2 Coaching**")
            c2_col1, c2_col2 = st.columns(2)
            with c2_col1:
                c2_coach = st.selectbox("Select Coach (Court 2):", options=avail_c2, key="same_c2_coach")
            with c2_col2:
                c2_pax = st.radio("Number of Pax for Coaching (Court 2):", options=[1, 2, 3, 4], format_func=lambda x: f"{x} Pax", horizontal=True, key="same_c2_pax")

            coaching_assignments[1] = {"coach_name": c1_coach, "pax": c1_pax}
            coaching_assignments[2] = {"coach_name": c2_coach, "pax": c2_pax}

    start_h = int(st.session_state["c1_start_time"].split(":")[0])
    dur_val = st.session_state["c1_play_duration"]
    s_str = st.session_state["c1_start_time"]
    e_str = st.session_state["c1_end_time"]

    court_configs.append({
        "court_num": 1,
        "start_hour": start_h,
        "duration": dur_val,
        "start_str": s_str,
        "end_str": e_str,
        "include_drilling": c_drilling and (drill_court_target in ["Court 1 Only", "Both Courts"]),
        "drilling_pax": c_drill_pax if (c_drilling and drill_court_target in ["Court 1 Only", "Both Courts"]) else 0,
        "include_coaching": c_coaching and (coach_court_target in ["Court 1 Only", "Both Courts"]),
        "coach_name": coaching_assignments.get(1, {}).get("coach_name", ""),
        "coaching_pax": coaching_assignments.get(1, {}).get("pax", 0),
        "regular_pax": 0
    })

    court_configs.append({
        "court_num": 2,
        "start_hour": start_h,
        "duration": dur_val,
        "start_str": s_str,
        "end_str": e_str,
        "include_drilling": c_drilling and (drill_court_target in ["Court 2 Only", "Both Courts"]),
        "drilling_pax": c_drill_pax if (c_drilling and drill_court_target in ["Court 2 Only", "Both Courts"]) else 0,
        "include_coaching": c_coaching and (coach_court_target in ["Court 2 Only", "Both Courts"]),
        "coach_name": coaching_assignments.get(2, {}).get("coach_name", ""),
        "coaching_pax": coaching_assignments.get(2, {}).get("pax", 0),
        "regular_pax": 0
    })

else:
    # --- 1 COURT or 2 COURTS - DIFF TIME CONFIGURATION ---
    num_forms = 2 if court_option == "2 Courts - Diff Time" else 1

    for c in range(1, num_forms + 1):
        if court_option == "2 Courts - Diff Time":
            st.markdown(f"#### 🏟️ Court {c} Configuration")
        
        start_key = f"c{c}_start_time"
        dur_key = f"c{c}_play_duration"
        end_key = f"c{c}_end_time"
        drill_key = f"c{c}_include_drilling"
        drill_pax_key = f"c{c}_drilling_pax"
        coach_key = f"c{c}_include_coaching"
        coach_name_key = f"c{c}_coach_name"
        coach_pax_key = f"c{c}_coaching_pax"

        if start_key not in st.session_state:
            st.session_state[start_key] = "17:00"

        if dur_key not in st.session_state:
            st.session_state[dur_key] = 2 if c == 1 else (3 if num_forms > 1 else 2)

        if end_key not in st.session_state:
            start_h = int(st.session_state[start_key].split(":")[0])
            st.session_state[end_key] = get_end_str(start_h, st.session_state[dur_key])

        def make_start_callback(c_num):
            def cb():
                sk = f"c{c_num}_start_time"
                dk = f"c{c_num}_play_duration"
                ek = f"c{c_num}_end_time"
                sh = int(st.session_state[sk].split(":")[0])
                dur = st.session_state.get(dk, 1)
                st.session_state[ek] = get_end_str(sh, dur)
            return cb

        def make_dur_callback(c_num):
            def cb():
                sk = f"c{c_num}_start_time"
                dk = f"c{c_num}_play_duration"
                ek = f"c{c_num}_end_time"
                sh = int(st.session_state[sk].split(":")[0])
                dur = st.session_state[dk]
                st.session_state[ek] = get_end_str(sh, dur)
            return cb

        def make_end_callback(c_num):
            def cb():
                sk = f"c{c_num}_start_time"
                dk = f"c{c_num}_play_duration"
                ek = f"c{c_num}_end_time"
                st.session_state[dk] = compute_duration(
                    st.session_state[sk], 
                    st.session_state[ek]
                )
            return cb

        def make_drill_toggle_cb(c_num):
            def cb():
                if st.session_state[f"c{c_num}_include_drilling"]:
                    st.session_state[f"c{c_num}_include_coaching"] = False
            return cb

        def make_coach_toggle_cb(c_num):
            def cb():
                if st.session_state[f"c{c_num}_include_coaching"]:
                    st.session_state[f"c{c_num}_include_drilling"] = False
            return cb

        s_col, d_col, e_col = st.columns(3)
        with s_col:
            st.selectbox("Start Time", time_options, key=start_key, on_change=make_start_callback(c))
        with d_col:
            st.selectbox("Play Duration", options=list(range(1, 25)), format_func=lambda x: f"{x} hr" if x == 1 else f"{x} hrs", key=dur_key, on_change=make_dur_callback(c))
        with e_col:
            st.selectbox("End Time", options=end_time_options, key=end_key, on_change=make_end_callback(c))

        c_drilling = st.toggle("Include Drilling?", key=drill_key, disabled=st.session_state.get(coach_key, False), on_change=make_drill_toggle_cb(c))
        c_drill_pax = 0
        if c_drilling:
            c_drill_pax = st.radio("Number of Pax for Drilling:", options=[1, 2, 3, 4], format_func=lambda x: f"{x} Pax", horizontal=True, key=drill_pax_key)

        c_coaching = st.toggle("Include Coaching?", key=coach_key, disabled=st.session_state.get(drill_key, False), on_change=make_coach_toggle_cb(c))
        c_coach_name = ""
        c_coach_pax = 0

        if c_coaching:
            avail_coaches = ALL_COACHES.copy()
            if court_option == "2 Courts - Diff Time":
                other_court = 2 if c == 1 else 1
                other_coaching = st.session_state.get(f"c{other_court}_include_coaching", False)
                other_coach = st.session_state.get(f"c{other_court}_coach_name", "")

                if is_overlapping and other_coaching and other_coach in avail_coaches:
                    avail_coaches.remove(other_coach)

            if coach_name_key not in st.session_state or st.session_state[coach_name_key] not in avail_coaches:
                st.session_state[coach_name_key] = avail_coaches[0]

            coach_col1, coach_col2 = st.columns(2)
            with coach_col1:
                c_coach_name = st.selectbox("Select Coach:", options=avail_coaches, key=coach_name_key)
            with coach_col2:
                c_coach_pax = st.radio("Number of Pax for Coaching:", options=[1, 2, 3, 4], format_func=lambda x: f"{x} Pax", horizontal=True, key=coach_pax_key)

        court_configs.append({
            "court_num": c,
            "start_hour": int(st.session_state[start_key].split(":")[0]),
            "duration": st.session_state[dur_key],
            "start_str": st.session_state[start_key],
            "end_str": st.session_state[end_key],
            "include_drilling": c_drilling,
            "drilling_pax": c_drill_pax,
            "include_coaching": c_coaching,
            "coach_name": c_coach_name,
            "coaching_pax": c_coach_pax,
            "regular_pax": 0
        })

# --- CALCULATION ---
court_fee = 0
total_drilling_fee = 0
total_coaching_fee = 0
total_pax = 0
breakdown = []

for cfg in court_configs:
    c_num = cfg["court_num"]
    s_h = cfg["start_hour"]
    dur = cfg["duration"]
    
    if cfg["include_drilling"]:
        total_pax += cfg["drilling_pax"]
    elif cfg["include_coaching"]:
        total_pax += cfg["coaching_pax"]

    # Calculate court time fee across all hours
    for h in range(dur):
        slot_dt = datetime.combine(selected_date, time((s_h + h) % 24, 0)) + timedelta(days=(s_h + h) // 24)
        rate_per_court, category = get_hourly_rate(slot_dt)
        court_fee += rate_per_court
        
        next_slot_str = (slot_dt + timedelta(hours=1)).strftime('%H:%M')
        court_label = f"Court {c_num} Fee" if court_option != "1 Court" else "Court Fee"
        
        breakdown.append({
            "Item": f"{court_label} [{slot_dt.strftime('%H:%M')} – {next_slot_str}]",
            "Category": category,
            "Rate": f"Rp{rate_per_court:,.0f}"
        })

    # Calculate drilling fee
    if cfg["include_drilling"]:
        pax = cfg["drilling_pax"]
        drilling_hourly_rate = DRILLING_MAP[pax]
        c_drilling_fee = drilling_hourly_rate * dur
        total_drilling_fee += c_drilling_fee
        per_person_rate = drilling_hourly_rate / pax

        item_label = f"Drilling Fee Court {c_num}" if court_option != "1 Court" else "Drilling Fee"
        breakdown.append({
            "Item": f"{item_label} ({dur} hr{'s' if dur > 1 else ''})",
            "Category": f"Drilling ({pax} Pax @ Rp{per_person_rate:,.0f}/person/hr)",
            "Rate": f"Rp{c_drilling_fee:,.0f}"
        })

    # Calculate coaching fee
    if cfg["include_coaching"]:
        pax = cfg["coaching_pax"]
        c_name = cfg["coach_name"]
        rate_per_pax_hr = COACHING_MAP[c_name][pax]
        c_coaching_fee = rate_per_pax_hr * pax * dur
        total_coaching_fee += c_coaching_fee

        item_label = f"Coaching Fee Court {c_num}" if court_option != "1 Court" else "Coaching Fee"
        breakdown.append({
            "Item": f"{item_label} ({dur} hr{'s' if dur > 1 else ''})",
            "Category": f"{c_name} ({pax} Pax @ Rp{rate_per_pax_hr:,.0f}/person/hr)",
            "Rate": f"Rp{c_coaching_fee:,.0f}"
        })

total_fee = court_fee + total_drilling_fee + total_coaching_fee

# --- DIVIDER BEFORE SUMMARY ---
st.divider()

# --- SUMMARY & FEE DISPLAY ---
st.markdown("### 📋 Booking Summary")
st.write(f"📅 **Date:** {selected_date.strftime('%A, %d %B %Y')}")
st.write(f"🏟️ **Courts:** {court_option}")

for cfg in court_configs:
    prefix = f"Court {cfg['court_num']}" if court_option != "1 Court" else "Time"
    st.write(f"⏰ **{prefix}:** {cfg['start_str']} – {cfg['end_str']} ({cfg['duration']} hour{'s' if cfg['duration'] > 1 else ''})")
    if cfg["include_drilling"]:
        dr_prefix = f"Court {cfg['court_num']} Drilling" if court_option != "1 Court" else "Drilling"
        st.write(f"🎾 **{dr_prefix}:** Yes ({cfg['drilling_pax']} Pax for {cfg['duration']} hr{'s' if cfg['duration'] > 1 else ''})")
    elif cfg["include_coaching"]:
        co_prefix = f"Court {cfg['court_num']} Coaching" if court_option != "1 Court" else "Coaching"
        st.write(f"🧢 **{co_prefix}:** {cfg['coach_name']} ({cfg['coaching_pax']} Pax for {cfg['duration']} hr{'s' if cfg['duration'] > 1 else ''})")

# Breakdown Table
st.table(breakdown)

# Total Fee Display Logic
left_col, right_col = st.columns([1, 1.2])

with left_col:
    st.metric(label="Total Fee", value=f"Rp{total_fee:,.0f}")

with right_col:
    st.metric(
        label=f"Total Fee / Person ({total_pax} Total Pax)",
        value=f"Rp{total_fee / total_pax:,.0f}" if total_pax > 0 else "N/A"
    )
