import streamlit as st

st.set_page_config(page_title="PPP Padel", page_icon="🎾")

# Define pages pointing to your files in the pages/ folder
calculator_page = st.Page("pages/calculator.py", title="Calculator", icon="🧮")
promotions_page = st.Page("pages/promotions.py", title="Promotions", icon="🏷️")

# Build navigation menu
pg = st.navigation([calculator_page, promotions_page])
pg.run()
