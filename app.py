import streamlit as st

st.set_page_config(page_title="draft request menu PPP", page_icon="🎾")

# Automatically redirects root domain visitors to /calculator
st.switch_page("pages/calculator.py")
