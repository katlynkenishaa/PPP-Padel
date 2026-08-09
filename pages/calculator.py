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
    {"Time Slot": "22:00 – 00:00", "Price / Court / Hour": "Rp185,000", "Category": "Late Night"}
]

WEEKEND_RATES = [
    {"Time Slot": "06:00 – 07:00", "Price / Court / Hour": "Rp178,000", "Category": "Early Morning"},
    {"Time Slot": "07:00 – 22:00", "Price / Court / Hour": "Rp258,000", "Category": "All Day Weekend"},
    {"Time Slot": "22:00 – 00:00", "Price / Court / Hour": "Rp199,000", "Category": "Late Night"}
]

DRILLING_RATES_LIST = [
    {"Pax": "1 Pax", "Price / Hour": "Rp160,000", "Cost / Person / Hour": "Rp160,000"},
    {"Pax": "2 Pax", "Price / Hour": "Rp190,000", "Cost / Person / Hour": "Rp95,000"},
    {"Pax": "3 Pax", "Price / Hour": "Rp220,000", "Cost / Person / Hour": "Rp73,333"},
    {"Pax": "4 Pax", "Price / Hour": "Rp250,000", "Cost / Person / Hour": "Rp62,500"},
]

DRILLING_MAP = {1: 160000, 2: 190000, 3: 220000, 4: 250000}

def get_hourly_rate(booking_datetime):
    """Returns (price, category) for a single 1-hour slot starting at booking_datetime."""
    is_weekend = booking_datetime.weekday() in [5, 6]
    hour = booking_datetime.hour

    if not is_weekend:
        if 6 <= hour < 7:
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
        if 6 <= hour < 7:
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
    col1, col2, col3 = st.columns([1, 1, 1.2])
    with col1:
        st.markdown("**Weekdays**")
        st.dataframe(pd.DataFrame(WEEKDAY_RATES), hide_index=True, use_container_width=True)
    with col2:
        st.markdown("**Weekend (Saturday & Sunday)**")
        st.dataframe(pd.DataFrame(WEEKEND_RATES), hide_index=True, use_container_width=True)
    with col3:
        st.markdown("**Drilling Rates**")
        st.dataframe(pd.DataFrame(DRILLING_RATES_LIST), hide_index=True, use_container_width=True)

# --- CALCULATOR FORM ---
st.subheader("Court Booking Fee Calculator")

# 1. Date Input
selected_date = st.date_input("Select Date", value=date.today())

# 2. Number of Courts
num_courts = st.selectbox(
    "Number of Courts",
    options=[1, 2],
    format_func=lambda x: f"{x} Court" if x == 1 else f"{x} Courts"
)

# Helper function to compute end string
def get_end_str(start_h, dur):
    end_h = start_h + dur
    return "00:00" if end_h == 24 else f"{end_h:02d}:00"

# Time setup per court
court_configs = []
time_options = [f"{hour:02d}:00" for hour in range(6, 24)]

for c in range(1, num_courts + 1):
    if num_courts > 1:
        st.markdown(f"#### 🏟️ Court {c} Timing")
    
    start_key = f"c{c}_start_time"
    dur_key = f"c{c}_play_duration"
    end_key = f"c{c}_end_time"

    # Default values initialization
    if start_key not in st.session_state:
        st.session_state[start_key] = "17:00" if c == 1 else "17:00"

    start_h = int(st.session_state[start_key].split(":")[0])
    max_dur = 24 - start_h
    dur_opts = list(range(1, max_dur + 1))
    end_opts = [f"{h:02d}:00" for h in range(start_h + 1, 24)] + ["00:00"]

    if dur_key not in st.session_state or st.session_state[dur_key] not in dur_opts:
        st.session_state[dur_key] = 2 if c == 1 else (3 if num_courts > 1 else 2)

    if end_key not in st.session_state or st.session_state[end_key] not in end_opts:
        st.session_state[end_key] = get_end_str(start_h, st.session_state[dur_key])

    # Callbacks for synchronization
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

    # Render inputs
    s_col, d_col, e_col = st.columns(3)
    with s_col:
        st.selectbox("Start Time", time_options, key=start_key, on_change=make_start_callback(c))
    with d_col:
        st.selectbox("Play Duration", options=dur_opts, format_func=lambda x: f"{x} hr" if x == 1 else f"{x} hrs", key=dur_key, on_change=make_dur_callback(c))
    with e_col:
        st.selectbox("End Time", options=end_opts, key=end_key, on_change=make_end_callback(c))

    court_configs.append({
        "court_num": c,
        "start_hour": int(st.session_state[start_key].split(":")[0]),
        "duration": st.session_state[dur_key],
        "start_str": st.session_state[start_key],
        "end_str": st.session_state[end_key]
    })

# 3. Optional Drilling Toggle & Pax Selection
include_drilling = st.toggle("Include Drilling?")

drilling_fee = 0
drilling_pax = 0
per_person_drilling_rate = 0

# Determine total hours across courts for drilling calculation
total_booking_hours = max([cfg["duration"] for cfg in court_configs])

if include_drilling:
    drilling_pax = st.radio(
        "Number of Pax for Drilling:",
        options=[1, 2, 3, 4],
        format_func=lambda x: f"{x} Pax",
        horizontal=True
    )
    total_drilling_hourly_rate = DRILLING_MAP[drilling_pax]
    drilling_fee = total_drilling_hourly_rate * total_booking_hours
    per_person_drilling_rate = total_drilling_hourly_rate / drilling_pax

# --- CALCULATION ---
court_fee = 0
breakdown = []

for cfg in court_configs:
    c_num = cfg["court_num"]
    s_h = cfg["start_hour"]
    dur = cfg["duration"]
    
    for h in range(dur):
        slot_dt = datetime.combine(selected_date, time(s_h + h, 0))
        rate, category = get_hourly_rate(slot_dt)
        court_fee += rate
        
        next_slot_str = "00:00" if (s_h + h + 1) == 24 else (slot_dt + timedelta(hours=1)).strftime('%H:%M')
        court_label = f"Court {c_num} Fee" if num_courts > 1 else "Court Fee"
        
        breakdown.append({
            "Item": f"{court_label} [{slot_dt.strftime('%H:%M')} – {next_slot_str}]",
            "Category": category,
            "Rate": f"Rp{rate:,.0f}"
        })

if include_drilling:
    breakdown.append({
        "Item": f"Add-on Fee ({total_booking_hours} hr{'s' if total_booking_hours > 1 else ''})",
        "Category": f"Drilling ({drilling_pax} Pax @ Rp{per_person_drilling_rate:,.0f}/person/hr)",
        "Rate": f"Rp{drilling_fee:,.0f}"
    })

total_fee = court_fee + drilling_fee

# --- DIVIDER BEFORE SUMMARY ---
st.divider()

# --- SUMMARY & FEE DISPLAY ---
st.markdown("### 📋 Booking Summary")
st.write(f"📅 **Date:** {selected_date.strftime('%A, %d %B %Y')}")
st.write(f"🏟️ **Courts:** {num_courts} {'Court' if num_courts == 1 else 'Courts'}")

for cfg in court_configs:
    prefix = f"Court {cfg['court_num']}" if num_courts > 1 else "Time"
    st.write(f"⏰ **{prefix}:** {cfg['start_str']} – {cfg['end_str']} ({cfg['duration']} hour{'s' if cfg['duration'] > 1 else ''})")

if include_drilling:
    st.write(f"🎾 **Drilling:** Yes ({drilling_pax} Pax for {total_booking_hours} hr{'s' if total_booking_hours > 1 else ''})")

# Breakdown Table
st.table(breakdown)

# Total Fee Display Logic
left_col, right_col = st.columns([1, 1.2])

with left_col:
    st.metric(label="Total Fee", value=f"Rp{total_fee:,.0f}")

with right_col:
    if include_drilling:
        st.metric(
            label=f"Total Fee / Person ({drilling_pax} Pax)",
            value=f"Rp{total_fee / drilling_pax:,.0f}"
        )
    else:
        st.markdown("**Total Fee / Person**")
        pax_split_data = [
            {"Players": f"{p} Pax", "Fee / Person": f"Rp{total_fee / p:,.0f}"}
            for p in range(1, 9)
        ]
        st.dataframe(pd.DataFrame(pax_split_data), hide_index=True, use_container_width=True)
