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
    """Returns (price, category) for a single 1-hour slot starting at booking_datetime."""
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
    end_h = start_h + dur
    return "00:00" if end_h == 24 else f"{end_h:02d}:00"

time_options = [f"{hour:02d}:00" for hour in range(0, 24)]

# Helper overlap check
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
    reg_pax_key = f"c{c}_regular_pax"

    if start_key not in st.session_state:
        st.session_state[start_key] = "17:00"

    start_h = int(st.session_state[start_key].split(":")[0])
    max_dur = 24 - start_h
    dur_opts = list(range(1, max_dur + 1))
    end_opts = [f"{h:02d}:00" for h in range(start_h + 1, 24)] + ["00:00"]

    if dur_key not in st.session_state or st.session_state[dur_key] not in dur_opts:
        st.session_state[dur_key] = 2 if c == 1 else (3 if num_forms > 1 else 2)

    if end_key not in st.session_state or st.session_state[end_key] not in end_opts:
        st.session_state[end_key] = get_end_str(start_h, st.session_state[dur_key])

    # Callbacks for time synchronization
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
            sh = int(st.session_state[sk].split(":")[0])
            end_str = st.session_state[ek]
            eh = 24 if end_str == "00:00" else int(end_str.split(":")[0])
            st.session_state[dk] = eh - sh
        return cb

    # Mutual Exclusion Callbacks
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

    # Time Controls
    s_col, d_col, e_col = st.columns(3)
    with s_col:
        st.selectbox("Start Time", time_options, key=start_key, on_change=make_start_callback(c))
    with d_col:
        st.selectbox("Play Duration", options=dur_opts, format_func=lambda x: f"{x} hr" if x == 1 else f"{x} hrs", key=dur_key, on_change=make_dur_callback(c))
    with e_col:
        st.selectbox("End Time", options=end_opts, key=end_key, on_change=make_end_callback(c))

    # Drilling Controls
    c_drilling = st.toggle(
        "Include Drilling?",
        key=drill_key,
        disabled=st.session_state.get(coach_key, False),
        on_change=make_drill_toggle_cb(c)
    )
    c_drill_pax = 0
    if c_drilling:
        c_drill_pax = st.radio(
            "Number of Pax for Drilling:",
            options=[1, 2, 3, 4],
            format_func=lambda x: f"{x} Pax",
            horizontal=True,
            key=drill_pax_key
        )

    # Coaching Controls
    c_coaching = st.toggle(
        "Include Coaching?",
        key=coach_key,
        disabled=st.session_state.get(drill_key, False),
        on_change=make_coach_toggle_cb(c)
    )

    # Handle Coaching Inputs (Per Court if '2 Courts - Same Time')
    court_coaching_assignments = []
    if c_coaching:
        coaching_courts = [1, 2] if court_option == "2 Courts - Same Time" else [c]
        
        for cc in coaching_courts:
            c_coach_name_key = f"c{cc}_coach_name"
            c_coach_pax_key = f"c{cc}_coaching_pax"
            
            other_cc = 2 if cc == 1 else 1
            other_coach_selected = st.session_state.get(f"c{other_cc}_coach_name", "")

            avail_coaches = ALL_COACHES.copy()
            if (court_option == "2 Courts - Same Time" or is_overlapping) and len(coaching_courts) > 1:
                if other_coach_selected in avail_coaches:
                    avail_coaches.remove(other_coach_selected)

            if c_coach_name_key in st.session_state and st.session_state[c_coach_name_key] not in avail_coaches:
                st.session_state[c_coach_name_key] = avail_coaches[0]

            if court_option == "2 Courts - Same Time":
                st.markdown(f"**Court {cc} Coaching**")

            coach_col1, coach_col2 = st.columns(2)
            with coach_col1:
                selected_coach = st.selectbox(
                    "Select Coach:",
                    options=avail_coaches,
                    key=c_coach_name_key
                )
            with coach_col2:
                selected_pax = st.radio(
                    "Number of Pax for Coaching:",
                    options=[1, 2, 3, 4],
                    format_func=lambda x: f"{x} Pax",
                    horizontal=True,
                    key=c_coach_pax_key
                )
            
            court_coaching_assignments.append({
                "court_num": cc,
                "coach_name": selected_coach,
                "coaching_pax": selected_pax
            })

    # Regular Players Controls
    c_reg_pax = 0
    if not c_drilling and not c_coaching:
        c_reg_pax = st.radio(
            "Number of Players on this Court:" if court_option == "2 Courts - Diff Time" else "Number of Players:",
            options=[1, 2, 3, 4, 5, 6, 7, 8],
            format_func=lambda x: f"{x} Pax",
            horizontal=True,
            key=reg_pax_key
        )

    court_configs.append({
        "court_num": c,
        "start_hour": int(st.session_state[start_key].split(":")[0]),
        "duration": st.session_state[dur_key],
        "start_str": st.session_state[start_key],
        "end_str": st.session_state[end_key],
        "include_drilling": c_drilling,
        "drilling_pax": c_drill_pax,
        "include_coaching": c_coaching,
        "coaching_assignments": court_coaching_assignments,
        "regular_pax": c_reg_pax
    })

# --- CALCULATION ---
court_fee = 0
total_drilling_fee = 0
total_coaching_fee = 0
total_pax = 0
breakdown = []

multiplier = 2 if court_option == "2 Courts - Same Time" else 1

for cfg in court_configs:
    c_num = cfg["court_num"]
    s_h = cfg["start_hour"]
    dur = cfg["duration"]
    
    # Calculate pax count
    if cfg["include_drilling"]:
        total_pax += (cfg["drilling_pax"] * multiplier)
    elif cfg["include_coaching"]:
        for ca in cfg["coaching_assignments"]:
            total_pax += ca["coaching_pax"]
    else:
        total_pax += (cfg["regular_pax"] * multiplier)

    # Calculate court hourly rates
    for h in range(dur):
        slot_dt = datetime.combine(selected_date, time(s_h + h, 0))
        rate_per_court, category = get_hourly_rate(slot_dt)
        slot_total = rate_per_court * multiplier
        court_fee += slot_total
        
        next_slot_str = "00:00" if (s_h + h + 1) == 24 else (slot_dt + timedelta(hours=1)).strftime('%H:%M')
        
        if court_option == "2 Courts - Same Time":
            court_label = "Court Fee (2 Courts)"
        elif court_option == "2 Courts - Diff Time":
            court_label = f"Court {c_num} Fee"
        else:
            court_label = "Court Fee"
        
        breakdown.append({
            "Item": f"{court_label} [{slot_dt.strftime('%H:%M')} – {next_slot_str}]",
            "Category": category,
            "Rate": f"Rp{slot_total:,.0f}"
        })

    # Drilling Fee Calculation
    if cfg["include_drilling"]:
        pax = cfg["drilling_pax"]
        drilling_hourly_rate = DRILLING_MAP[pax]
        c_drilling_fee = drilling_hourly_rate * dur * multiplier
        total_drilling_fee += c_drilling_fee
        per_person_rate = drilling_hourly_rate / pax

        item_label = "Drilling Fee (2 Courts)" if court_option == "2 Courts - Same Time" else (f"Drilling Fee Court {c_num}" if court_option == "2 Courts - Diff Time" else "Drilling Fee")
        breakdown.append({
            "Item": f"{item_label} ({dur} hr{'s' if dur > 1 else ''})",
            "Category": f"Drilling ({pax} Pax @ Rp{per_person_rate:,.0f}/person/hr)",
            "Rate": f"Rp{c_drilling_fee:,.0f}"
        })

    # Coaching Fee Calculation
    if cfg["include_coaching"]:
        for ca in cfg["coaching_assignments"]:
            cc_num = ca["court_num"]
            pax = ca["coaching_pax"]
            c_name = ca["coach_name"]
            rate_per_pax_hr = COACHING_MAP[c_name][pax]
            c_coaching_fee = rate_per_pax_hr * pax * dur
            total_coaching_fee += c_coaching_fee

            item_label = f"Coaching Fee Court {cc_num}" if (court_option != "1 Court") else "Coaching Fee"
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
    prefix = f"Court {cfg['court_num']}" if court_option == "2 Courts - Diff Time" else "Time"
    st.write(f"⏰ **{prefix}:** {cfg['start_str']} – {cfg['end_str']} ({cfg['duration']} hour{'s' if cfg['duration'] > 1 else ''})")
    if cfg["include_drilling"]:
        dr_prefix = f"Court {cfg['court_num']} Drilling" if court_option == "2 Courts - Diff Time" else "Drilling"
        st.write(f"🎾 **{dr_prefix}:** Yes ({cfg['drilling_pax']} Pax for {cfg['duration']} hr{'s' if cfg['duration'] > 1 else ''})")
    elif cfg["include_coaching"]:
        for ca in cfg["coaching_assignments"]:
            co_prefix = f"Court {ca['court_num']} Coaching" if court_option != "1 Court" else "Coaching"
            st.write(f"🧢 **{co_prefix}:** {ca['coach_name']} ({ca['coaching_pax']} Pax for {cfg['duration']} hr{'s' if cfg['duration'] > 1 else ''})")
    else:
        pax_prefix = f"Court {cfg['court_num']} Players" if court_option == "2 Courts - Diff Time" else "Players"
        pax_val = cfg['regular_pax'] * multiplier
        st.write(f"👥 **{pax_prefix}:** {pax_val} Pax")

# Breakdown Table
st.table(breakdown)

# Total Fee Display Logic
left_col, right_col = st.columns([1, 1.2])

with left_col:
    st.metric(label="Total Fee", value=f"Rp{total_fee:,.0f}")

with right_col:
    st.metric(
        label=f"Total Fee / Person ({total_pax} Total Pax)",
        value=f"Rp{total_fee / total_pax:,.0f}"
    )
