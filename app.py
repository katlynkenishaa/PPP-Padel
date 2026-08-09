import streamlit as st

# Define pages pointing to files inside pages/ folder
calculator_page = st.Page(
    "pages/calculator.py",
    title="Calculator",
    icon="🧮",
    url_path="calculator",  # Forces URL to be /calculator
    default=False,           # Sets as default landing page
)

promotions_page = st.Page(
    "pages/promotions.py",
    title="Promotions",
    icon="🏷️",
    url_path="promotions",  # Forces URL to be /promotions
)

# Initialize navigation menu
pg = st.navigation([calculator_page, promotions_page])
pg.run()
