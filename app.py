import streamlit as st

st.set_page_config(page_title="draft request menu PPP", page_icon="🎾")

# Define pages linking directly to files in pages/
calculator_page = st.Page(
    "pages/calculator.py",
    title="Calculator",
    icon="🧮",
    url_path="calculator",  # Explicitly sets URL to /calculator
    default=True,           # Sets this as the default landing page
)

promotions_page = st.Page(
    "pages/promotions.py",
    title="Promotions",
    icon="🏷️",
    url_path="promotions",  # Explicitly sets URL to /promotions
)

# Render navigation menu in sidebar
pg = st.navigation([calculator_page, promotions_page])
pg.run()
