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

# 2. Start Time Dropdown (06:00 to 23:00)
time_options = [f"{hour:02d}:00" for hour in range(6, 24)]

# Callback when Start Time changes
def on_start_time_change():
    start_h = int(st.session_state.start_time.split(":")[0])
    dur = st.session_state.get("play_duration", 1)
    end_h = start_h + dur
    st.session_state.end_time = "00:00" if end_h == 24 else f"{end_h:02d}:00"

start_time_str = st.selectbox("Start Time", time_options, key="start_time", on_change=on_start_time_change)
start_hour = int(start_time_str.split(":")[0])

# Dynamic Options: End Time can go up to 24:00 (00:00)
max_duration = 24 - start_hour
duration_options = list(range(1, max_duration + 1))
end_time_options = [f"{h:02d}:00" for h in range(start_hour + 1, 24)] + ["00:00"]

if "play_duration" not in st.session_state or st.session_state.play_duration not in duration_options:
    st.session_state.play_duration = 1

def end_str_from_dur(dur):
    end_h = start_hour + dur
    return "00:00" if end_h == 24 else f"{end_h:02d}:00"

if "end_time" not in st.session_state or st.session_state.end_time not in end_time_options:
    st.session_state.end_time = end_str_from_dur(st.session_state.play_duration)

# Sync Callbacks
def update_from_duration():
    st.session_state.end_time = end_str_from_dur(st.session_state.play_duration)

def update_from_end_time():
    end_str = st.session_state.end_time
    end_h = 24 if end_str == "00:00" else int(end_str.split(":")[0])
    st.session_state.play_duration = end_h - start_hour

# 3. Side-by-Side Play Duration & End Time
dur_col, end_col = st.columns(2)

with dur_col:
    st.selectbox(
        "Play Duration",
        options=duration_options,
        format_func=lambda x: f"{x} hour" if x == 1 else f"{x} hours",
        key="play_duration",
        on_change=update_from_duration
    )

with end_col:
    st.selectbox(
        "End Time",
        options=end_time_options,
        key="end_time",
        on_change=update_from_end_time
    )

duration = st.session_state.play_duration

# 4. Number of Courts Dropdown
num_courts = st.selectbox(
    "Number of Courts",
    options=[1, 2],
    format_func=lambda x: f"{x} Court" if x == 1 else f"{x} Courts"
)

# 5. Optional Drilling Toggle & Pax Selection
include_drilling = st.toggle("Include Drilling?")

drilling_fee = 0
drilling_pax = 0

if include_drilling:
    drilling_pax = st.radio(
        "Number of Pax for Drilling:",
        options=[1, 2, 3, 4],
        format_func=lambda x: f"{x} Pax",
        horizontal=True
    )
    drilling_hourly_rate = DRILLING_MAP[drilling_pax]
    drilling_fee = drilling_hourly_rate * duration

# --- CALCULATION ---
court_fee = 0
breakdown = []

for h in range(duration):
    slot_dt = datetime.combine(selected_date, time(start_hour + h, 0))
    rate_per_court, category = get_hourly_rate(slot_dt)
    slot_total = rate_per_court * num_courts
    court_fee += slot_total
    
    court_label = f"Court Fee ({num_courts} {'Court' if num_courts == 1 else 'Courts'})"
    next_slot_str = "00:00" if (start_hour + h + 1) == 24 else (slot_dt + timedelta(hours=1)).strftime('%H:%M')
    
    breakdown.append({
        "Item": f"{court_label} [{slot_dt.strftime('%H:%M')} – {next_slot_str}]",
        "Category": category,
        "Rate": f"Rp{slot_total:,.0f}"
    })

if include_drilling:
    breakdown.append({
        "Item": f"Add-on Fee ({duration} hr{'s' if duration > 1 else ''})",
        "Category": f"Drilling ({drilling_pax} Pax @ Rp{DRILLING_MAP[drilling_pax]:,.0f}/hr)",
        "Rate": f"Rp{drilling_fee:,.0f}"
    })

total_fee = court_fee + drilling_fee
display_end_time = end_str_from_dur(duration)

# --- DIVIDER BEFORE SUMMARY ---
st.divider()

# --- SUMMARY & FEE DISPLAY ---
st.markdown("### 📋 Booking Summary")
st.write(f"📅 **Date:** {selected_date.strftime('%A, %d %B %Y')}")
st.write(f"🏟️ **Courts:** {num_courts} {'Court' if num_courts == 1 else 'Courts'}")
st.write(f"⏰ **Time:** {start_time_str} – {display_end_time} ({duration} hour{'s' if duration > 1 else ''})")
if include_drilling:
    st.write(f"🎾 **Drilling:** Yes ({drilling_pax} Pax for {duration} hr{'s' if duration > 1 else ''})")

# Breakdown Table
st.table(breakdown)

# Total Fee Display
st.metric(label="Total Fee", value=f"Rp{total_fee:,.0f}")
