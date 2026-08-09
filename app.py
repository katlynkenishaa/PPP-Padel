import streamlit as st
from datetime import datetime, date, time, timedelta

st.set_page_config(page_title="draft request menu PPP", page_icon="🎾")

st.title("🎾 draft request menu PPP")

# --- PRICING LOGIC ---
def get_hourly_rate(booking_datetime):
    """
    Returns (price, category) for a single 1-hour slot starting at booking_datetime.
    """
    is_weekend = booking_datetime.weekday() in [5, 6]  # 5 = Saturday, 6 = Sunday
    hour = booking_datetime.hour

    if not is_weekend:
        # Weekday Pricing
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
        # Weekend Pricing (Saturday & Sunday)
        if 6 <= hour < 7:
            return 178000, "Early Morning"
        elif 7 <= hour < 22:
            return 258000, "All Day Weekend"
        elif 22 <= hour < 24:
            return 199000, "Late Night"
        else:
            return 0, "Closed"

# --- CALCULATOR INTERFACE ---
st.subheader("🧮 Court Booking Fee Calculator")

# 1. Date Input
selected_date = st.date_input("Select Date", value=date.today())

# 2. Start Time Dropdown (06:00 to 23:00)
time_options = [f"{hour:02d}:00" for hour in range(6, 24)]
start_time_str = st.selectbox("Start Time", time_options)

# 3. Play Duration (1 or 2 hours)
duration = st.radio(
    "Play Duration", 
    options=[1, 2], 
    format_func=lambda x: f"{x} hour" if x == 1 else f"{x} hours", 
    horizontal=True
)

# --- CALCULATION ---
start_hour = int(start_time_str.split(":")[0])
total_fee = 0
breakdown = []

for h in range(duration):
    slot_dt = datetime.combine(selected_date, time(start_hour + h, 0))
    rate, category = get_hourly_rate(slot_dt)
    total_fee += rate
    breakdown.append({
        "Slot": f"{slot_dt.strftime('%H:%M')} – {(slot_dt + timedelta(hours=1)).strftime('%H:%M')}",
        "Category": category,
        "Rate": f"Rp{rate:,.0f}"
    })

end_dt = datetime.combine(selected_date, time(start_hour, 0)) + timedelta(hours=duration)

st.divider()

# --- SUMMARY & FEE DISPLAY ---
st.markdown("### 📋 Booking Summary")
st.write(f"📅 **Date:** {selected_date.strftime('%A, %d %B %Y')}")
st.write(f"⏰ **Time:** {start_time_str} – {end_dt.strftime('%H:%M')} ({duration} hour{'s' if duration > 1 else ''})")

# Breakdown Table
st.table(breakdown)

# Total Fee Display
st.metric(label="Total Fee", value=f"Rp{total_fee:,.0f}")
