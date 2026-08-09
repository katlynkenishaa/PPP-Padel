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
    {"Pax": "1 Pax", "Price": "Rp160,000"},
    {"Pax": "2 Pax", "Price": "Rp190,000"},
    {"Pax": "3 Pax", "Price": "Rp220,000"},
    {"Pax": "4 Pax", "Price": "Rp250,000"},
]

DRILLING_MAP = {1: 160000, 2: 190000, 3: 220000, 4: 250000}

def get_hourly_rate(booking_datetime):
    """Returns (price, category) for a single 1-hour slot starting at booking_datetime."""
    is_weekend = booking_datetime.weekday() in [5, 6]  # 5 = Saturday, 6 = Sunday
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
st.subheader("📊 Base Pricing Rate Card")
col1, col2, col3 = st.columns(3)
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
start_time_str = st.selectbox("Start Time", time_options)

# 3. Play Duration Dropdown (1 to 5 hours)
duration = st.selectbox(
    "Play Duration", 
    options=[1, 2, 3, 4, 5], 
    format_func=lambda x: f"{x} hour" if x == 1 else f"{x} hours"
)

# 4. Optional Drilling Toggle & Pax Selection
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
    drilling_fee = DRILLING_MAP[drilling_pax]

# --- CALCULATION ---
start_hour = int(start_time_str.split(":")[0])
court_fee = 0
breakdown = []

for h in range(duration):
    slot_dt = datetime.combine(selected_date, time(start_hour + h, 0))
    rate, category = get_hourly_rate(slot_dt)
    court_fee += rate
    breakdown.append({
        "Item": f"Court Fee ({slot_dt.strftime('%H:%M')} – {(slot_dt + timedelta(hours=1)).strftime('%H:%M')})",
        "Category": category,
        "Rate": f"Rp{rate:,.0f}"
    })

if include_drilling:
    breakdown.append({
        "Item": "Add-on Fee",
        "Category": f"Drilling ({drilling_pax} Pax)",
        "Rate": f"Rp{drilling_fee:,.0f}"
    })

total_fee = court_fee + drilling_fee
end_dt = datetime.combine(selected_date, time(start_hour, 0)) + timedelta(hours=duration)

# --- DIVIDER BEFORE SUMMARY ---
st.divider()

# --- SUMMARY & FEE DISPLAY ---
st.markdown("### 📋 Booking Summary")
st.write(f"📅 **Date:** {selected_date.strftime('%A, %d %B %Y')}")
st.write(f"⏰ **Time:** {start_time_str} – {end_dt.strftime('%H:%M')} ({duration} hour{'s' if duration > 1 else ''})")
if include_drilling:
    st.write(f"🎾 **Drilling:** Yes ({drilling_pax} Pax)")

# Breakdown Table
st.table(breakdown)

# Total Fee Display
st.metric(label="Total Fee", value=f"Rp{total_fee:,.0f}")
