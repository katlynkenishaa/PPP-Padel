# --- CALCULATOR FORM ---
st.subheader("Court Booking Fee Calculator")

# 1. Date Input
selected_date = st.date_input("Select Date", value=date.today())

# 2. Start Time Dropdown (06:00 to 23:00)
time_options = [f"{hour:02d}:00" for hour in range(6, 24)]
start_time_str = st.selectbox("Start Time", time_options)
start_hour = int(start_time_str.split(":")[0])

# 3. Input Mode Selection (Play Duration vs. End Time)
input_mode = st.radio(
    "Calculate By:",
    options=["Play Duration", "End Time"],
    horizontal=True
)

if input_mode == "Play Duration":
    # Duration options up to max remaining operational hours in the day
    max_duration = min(5, 24 - start_hour)
    duration = st.selectbox(
        "Play Duration", 
        options=list(range(1, max_duration + 1)), 
        format_func=lambda x: f"{x} hour" if x == 1 else f"{x} hours"
    )
else:
    # End Time options from (start_hour + 1) up to 24:00 (capped at start + 5 hours)
    end_time_options = [f"{(start_hour + h):02d}:00" for h in range(1, min(6, 25 - start_hour))]
    end_time_str = st.selectbox("End Time", end_time_options)
    end_hour = int(end_time_str.split(":")[0])
    duration = end_hour - start_hour

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
    drilling_fee = DRILLING_MAP[drilling_pax]
