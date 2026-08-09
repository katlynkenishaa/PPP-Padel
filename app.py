import streamlit as st

# 1. Define the pages from the pages/ folder
home_page = st.Page(
    "app.py", 
    title="Home", 
    icon="🏠",
    url_path=""  # Root URL (https://ppp-padel.streamlit.app)
)

calculator_page = st.Page(
    "pages/calculator.py", 
    title="Calculator", 
    icon="🧮", 
    url_path="calculator"  # Forces URL to https://ppp-padel.streamlit.app/calculator
)

promotions_page = st.Page(
    "pages/promotions.py", 
    title="Promotions", 
    icon="🏷️", 
    url_path="promotions"  # Forces URL to https://ppp-padel.streamlit.app/promotions
)

# 2. Setup navigation
pg = st.navigation({
    "Menu": [home_page, calculator_page, promotions_page]
})

# 3. Only run the landing page content if user is on the Home page
if pg.selected == home_page:
    st.set_page_config(page_title="draft request menu PPP", page_icon="🎾")
    st.title("🎾 draft request menu PPP")
    st.info("👈 Choose Sidebar")
else:
    pg.run()
