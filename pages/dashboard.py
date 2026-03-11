import streamlit as st
import database as db
from views.student import student_view
from views.admin import admin_view
from views.leaderboard import leaderboard_view

def dashboard_page():
    # Sidebar Branding
    st.sidebar.markdown('<div class="sidebar-brand">🚀 PlaceWise</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"### Welcome,\n{st.session_state.name}")
    st.sidebar.markdown(f"**Role:** {st.session_state.role.capitalize()}")
    
    options = ["🏠 Home", "🏆 Leaderboard"]
    choice = st.sidebar.radio("Navigate", options)
    
    if st.sidebar.button("Logout", type="primary"):
        st.session_state.logged_in = False
        st.session_state.authenticated = False
        st.rerun()
    
    st.sidebar.divider()
    
    # --- ROUTING ---
    if choice == "🏠 Home":
        if st.session_state.role == "student":
            student_view()
        elif st.session_state.role == "admin":
            admin_view()
            
    elif choice == "🏆 Leaderboard":
        leaderboard_view()

if __name__ == "__main__":
    if st.session_state.get("authenticated"):
        dashboard_page()
    else:
        st.error("Please login first.")
