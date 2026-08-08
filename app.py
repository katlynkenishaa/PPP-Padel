import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

st.set_page_config(page_title="Padel Voucher Monitor", page_icon="🎾")

# --- 🔒 PIN LOGIN SCREEN ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Create a variable in memory to hold the digits as they are typed
if "entered_pin" not in st.session_state:
    st.session_state["entered_pin"] = ""

# Functions to handle button clicks
def add_digit(digit):
    if len(st.session_state["entered_pin"]) < 4:
        st.session_state["entered_pin"] += str(digit)

def clear_pin():
    st.session_state["entered_pin"] = ""

if not st.session_state["authenticated"]:
    st.title("🔒 Staff Login")
    
    # --- CHANGED: Display actual numbers instead of black circles ---
    entered_digits = st.session_state["entered_pin"]
    # Join the typed numbers with spaces, then add the remaining white circles
    display_pin = " ".join(entered_digits) + " " + "⚪ " * (4 - len(entered_digits))
    
    st.markdown(f"<h2 style='text-align: center; letter-spacing: 10px;'>{display_pin.strip()}</h2>", unsafe_allow_html=True)
    st.write("") # Small spacer
    # ----------------------------------------------------------------
    
    # Create a centered 3x4 grid for the Numpad using columns
    _, col1, col2, col3, _ = st.columns([1, 2, 2, 2, 1])
    
    with col1:
        st.button("1", on_click=add_digit, args=("1",), use_container_width=True)
        st.button("4", on_click=add_digit, args=("4",), use_container_width=True)
        st.button("7", on_click=add_digit, args=("7",), use_container_width=True)
        st.button("C", on_click=clear_pin, use_container_width=True) # Clear button
        
    with col2:
        st.button("2", on_click=add_digit, args=("2",), use_container_width=True)
        st.button("5", on_click=add_digit, args=("5",), use_container_width=True)
        st.button("8", on_click=add_digit, args=("8",), use_container_width=True)
        st.button("0", on_click=add_digit, args=("0",), use_container_width=True)
        
    with col3:
        st.button("3", on_click=add_digit, args=("3",), use_container_width=True)
        st.button("6", on_click=add_digit, args=("6",), use_container_width=True)
        st.button("9", on_click=add_digit, args=("9",), use_container_width=True)
        
        # The OK/Login Button
        if st.button("OK", type="primary", use_container_width=True):
            if st.session_state["entered_pin"] == str(st.secrets["staff_pin"]):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect PIN. Please try again.")
                st.session_state["entered_pin"] = "" # Auto-clears the pad on failure
                
    st.stop() # This stops the rest of the app from loading until unlocked!
# --- END PIN LOGIN SCREEN ---

# --- 🎾 MAIN APP (Only runs if authenticated) ---
st.title("🎾 Padel Court Voucher Monitor")

# Connect to Google Sheets securely using Streamlit Secrets
@st.cache_resource
def connect_to_sheet():
    # Load credentials from the secure background environment
    creds_dict = json.loads(st.secrets["google_credentials"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_url(st.secrets["sheet_url"]).sheet1

try:
    sheet = connect_to_sheet()
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    st.stop()

# Build the Web Interface Tabs
tab1, tab2 = st.tabs(["📝 Record Visit", "🔍 Check Customer"])

with tab1:
    rec_id = st.text_input("Customer ID", key="rec_id")
    rec_name = st.text_input("Customer Name")
    
    rec_voucher = st.selectbox("Voucher Code", ["Promo A", "Promo B", "No Promo"])
    
    if st.button("Save Visit to Google Sheets", type="primary"):
        if not rec_id or not rec_name:
            st.error("Please enter both Customer ID and Name.")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([str(rec_id).strip(), rec_name.strip(), rec_voucher, current_time])
            st.success(f"✅ Recorded visit for {rec_name}!")

with tab2:
    check_id = st.text_input("Enter Customer ID:")
    if st.button("Search", type="primary"):
        if not check_id:
            st.warning("Please enter an ID.")
        else:
            df = pd.DataFrame(sheet.get_all_records())
            if not df.empty and 'Customer ID' in df.columns:
                df['Customer ID'] = df['Customer ID'].astype(str).str.strip()
                matches = df[df['Customer ID'] == str(check_id).strip()]
                if not matches.empty:
                    st.warning(f"🟡 RETURNING CUSTOMER: Visited {len(matches)} time(s) before!")
                    st.dataframe(matches[['Date', 'Customer Name', 'Voucher Code']], use_container_width=True)
                else:
                    st.success("🟢 NEW CUSTOMER: No previous records found.")
            else:
                st.success("🟢 NEW CUSTOMER: No previous records found.")
