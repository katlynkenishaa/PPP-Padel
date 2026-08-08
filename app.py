import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

st.set_page_config(page_title="Padel Voucher Monitor", page_icon="🎾")

# --- 🔒 PIN LOGIN SCREEN ---
# Check if the user is already authenticated in this session
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# If not authenticated, show the login screen and stop the app
if not st.session_state["authenticated"]:
    st.title("🔒 Staff Login")
    pin_input = st.text_input("Enter Staff PIN:", type="password")
    
    if st.button("Login", type="primary"):
        if pin_input == str(st.secrets["staff_pin"]):
            st.session_state["authenticated"] = True
            st.rerun()  # Refresh the page to load the main app
        else:
            st.error("Incorrect PIN. Please try again.")
            
    st.stop()  # This strictly prevents the code below from running

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
