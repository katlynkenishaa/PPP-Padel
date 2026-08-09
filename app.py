import streamlit as st

st.set_page_config(
    page_title="draft request menu PPP", 
    page_icon="🎾", 
    initial_sidebar_state="expanded"
)

# Adding sidebar element forces Streamlit to render the navigation menu
st.sidebar.title("Navigation")
st.sidebar.info("Select a page above.")

st.title("🎾 Welcome to draft request menu PPP")
st.info("👈 Please select a tool from the sidebar menu on the left.")
