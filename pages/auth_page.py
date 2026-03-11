import streamlit as st
import streamlit_antd_components as sac
import database as db

def login_form():
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            user = db.verify_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.authenticated = True # New flag as requested
                st.session_state.username = username
                st.session_state.role = user['role']
                st.session_state.name = user['name']
                st.session_state.roll_no = user['roll_no']
                st.rerun()
            else:
                sac.alert(label='Error', description='Invalid Username or Password', variant='filled', color='error', closable=True)

def signup_form():
    with st.form("signup_form"):
        new_user = st.text_input("Desired Username")
        new_pass = st.text_input("Password", type="password")
        name = st.text_input("Full Name")
        roll_no = st.text_input("Roll Number")
        submit = st.form_submit_button("Create Account", use_container_width=True)
        
        if submit:
            if new_user and new_pass and name and roll_no:
                if db.create_user(new_user, new_pass, "student", name, roll_no):
                    sac.alert(label='Success', description='Account created successfully! You can now login.', variant='filled', color='success', closable=True)
                else:
                    sac.alert(label='Error', description='Username already exists.', variant='filled', color='error', closable=True)
            else:
                sac.alert(label='Warning', description='Please fill all required fields.', variant='filled', color='warning', closable=True)

def auth_page():
    # Center the card
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        # Title outside the form but inside the styled column
        st.markdown("<h2 style='text-align: center;'>🎓 PlaceWise</h2>", unsafe_allow_html=True)
        
        # SAC Tabs
        choice = sac.tabs([
            sac.TabsItem(label='Login', icon='key'),
            sac.TabsItem(label='Sign Up', icon='person-plus'),
        ], align='center', variant='toggle', use_container_width=True)
        
        if choice == 'Login':
            login_form()
        else:
            signup_form()

if __name__ == "__main__":
    auth_page()
