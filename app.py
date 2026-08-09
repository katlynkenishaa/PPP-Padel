import streamlit as st

# 1. Define the pages pointing to your scripts
home_page = st.Page(
    "pages/home.py", 
    title="Home", 
    icon="🏠",
    url_path="",
    default=True  # Fixes the empty url_path error
)

calculator_page = st.Page(
    "pages/calculator.py", 
    title="Calculator", 
    icon="🧮", 
    url_path="calculator"
)

promotions_page = st.Page(
    "pages/promotions.py", 
    title="Promotions", 
    icon="🏷️", 
    url_path="promotions"
)

# 2. Setup navigation
pg = st.navigation([home_page, calculator_page, promotions_page])
pg.run()
