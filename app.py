import streamlit as st
import database as db

# --- INITIAL SETUP ---
st.set_page_config(page_title="PlaceWise", page_icon="🎓", layout="wide")

# Initialize Database
db.init_db()

# --- SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'name' not in st.session_state:
    st.session_state.name = ""

# --- CSS DEFINITIONS ---
def inject_login_css():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            background-attachment: fixed !important;
        }
        
        /* Style the container that acts as our card */
        [data-testid="stVerticalBlock"] > div:has(div > [data-testid="stForm"]) {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 20px !important;
            padding: 2rem !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2) !important;
        }

        h2 { color: #212529 !important; font-weight: 800 !important; margin-bottom: 0 !important; }
        p, span, label { color: #495057 !important; font-weight: 500 !important; }
        
        .ant-tabs-tab-btn { color: #6c757d !important; font-weight: 600 !important; }
        .ant-tabs-tab-active .ant-tabs-tab-btn { color: #667eea !important; font-weight: 800 !important; }
        .ant-tabs-ink-bar { background: #667eea !important; }
        
        .stButton>button { 
            border-radius: 12px; height: 3.4em; border: none; font-weight: 700;
            background: #667eea !important; color: #FFFFFF !important; 
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover { 
            background: #4CAF50 !important; 
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
        }
        </style>
        """, unsafe_allow_html=True)

def inject_dashboard_css():
    st.markdown("""
        <style>
        /* Force White Background */
        .stApp {
            background-color: #FFFFFF !important;
            background-image: none !important;
        }
        
        /* Sidebar Refinement */
        [data-testid="stSidebar"] { 
            background-color: #F8F9FA !important; 
            border-right: 1px solid #E9ECEF !important;
        }
        
        /* Universal Text Color */
        h1, h2, h3, p, span, label, div { 
            color: #212529 !important;
            font-family: 'Inter', sans-serif;
        }
        
        /* SAC Tabs on White Background */
        .ant-tabs-nav-list { 
            background: #F1F3F5 !important; 
            border-radius: 10px !important; 
            padding: 4px !important; 
        }
        .ant-tabs-tab-btn { color: #495057 !important; font-weight: 600 !important; }
        .ant-tabs-tab-active .ant-tabs-tab-btn { color: #007BFF !important; }
        .ant-tabs-ink-bar { background: #007BFF !important; }
        
        /* Dashboard Buttons */
        .stButton>button { 
            border-radius: 10px; height: 3em; 
            background-color: #FFFFFF !important; 
            color: #212529 !important; 
            border: 1px solid #DEE2E6 !important;
        }
        .stButton>button:hover { 
            background-color: #F8F9FA !important; 
            border-color: #ADB5BD !important; 
        }
        
        /* Logout/Primary Buttons */
        .stButton>button[kind="primary"] {
            background-color: #FF4B4B !important; 
            color: white !important; 
            border: none !important;
        }
        
        .sidebar-brand { 
            font-size: 24px; font-weight: 800; color: #007BFF; 
            padding: 1rem 0; text-align: center; border-bottom: 1px solid #E9ECEF; 
        }
        </style>
        """, unsafe_allow_html=True)

# --- ROUTING LOGIC ---
def main():
    if not st.session_state.authenticated:
        inject_login_css()
        from pages.auth_page import auth_page
        auth_page()
    else:
        inject_dashboard_css()
        from pages.dashboard import dashboard_page
        dashboard_page()

if __name__ == "__main__":
    main()
