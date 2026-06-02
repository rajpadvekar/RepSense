import os
import sys
import streamlit as st

# Add the backend folder to sys.path to enable clean imports on execution
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database.db_manager import DBManager
from services.auth_service import AuthService

# Initialize database schema
DBManager.init_db()

# Configure Streamlit page options
st.set_page_config(
    page_title="RepSense - AI Fitness Coach",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global CSS custom theme styles
css_file = os.path.join(backend_dir, "static", "custom_styles.css")
if os.path.exists(css_file):
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Import views (defined as callable functions)
from views.landing import show_landing
from views.live_workout import show_live_workout
from views.planner import show_planner
from views.dashboard import show_dashboard
from views.library import show_library
from views.ai_coach import show_ai_coach
from views.profile import show_profile
from views.settings import show_settings


def render_auth_page():
    """
    Renders login and signup panels in case the user session is unauthenticated.
    """
    st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>REPSENSE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888888; font-size: 14px; letter-spacing: 0.15em; margin-bottom: 40px;'>AI THAT WATCHES EVERY REP</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.8, 1])
    
    with col2:
        st.markdown("<div class='glass-card glow-card'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 SIGN IN", "📝 REGISTER"])
        
        with tab1:
            st.write("")
            login_username = st.text_input("Username", key="login_user_key")
            login_password = st.text_input("Password", type="password", key="login_pass_key")
            
            st.write("")
            if st.button("Log In", key="login_submit_btn"):
                user = AuthService.login_user(login_username, login_password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")

        with tab2:
            st.write("")
            reg_username = st.text_input("Username", key="reg_user_key")
            reg_email = st.text_input("Email Address", key="reg_email_key")
            reg_password = st.text_input("Password", type="password", key="reg_pass_key")
            
            st.write("")
            if st.button("Create Account", key="reg_submit_btn"):
                if not reg_username or not reg_email or not reg_password:
                    st.warning("Please fill out all fields.")
                else:
                    new_user_id = AuthService.register_user(reg_username, reg_password, reg_email)
                    if new_user_id:
                        st.success("Account successfully created! Please log in above.")
                    else:
                        st.error("Registration failed. Username or email may already be taken.")
                        
        st.markdown("</div>", unsafe_allow_html=True)


def main():
    # If not logged in, render authentication page
    if not st.session_state.authenticated:
        render_auth_page()
        return

    # User is logged in, show dashboard sidebar navigation
    user = st.session_state.user
    
    st.sidebar.markdown(
        f"<h2 style='margin-bottom: 2px; color: #ffffff;'>RepSense</h2>"
        f"<p style='font-size: 10px; color: #f5a623; letter-spacing: 0.1em; margin-bottom: 20px;'>HELLO, {user['username'].upper()}</p>",
        unsafe_allow_html=True
    )

    # Main sidebar page list selector
    page = st.sidebar.radio(
        "NAVIGATION",
        ["Home", "Live Workout", "Workout & Diet Planner", "Analytics Dashboard", "Exercise Library", "AI Coach Chat", "My Profile", "Settings"]
    )
    
    st.sidebar.write("---")
    
    # Log out button at sidebar bottom
    if st.sidebar.button("Logout", key="logout_sidebar_btn"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.current_page = "Home"
        st.rerun()

    # Route page selection to display functions
    if page == "Home":
        show_landing()
    elif page == "Live Workout":
        show_live_workout()
    elif page == "Workout & Diet Planner":
        show_planner()
    elif page == "Analytics Dashboard":
        show_dashboard()
    elif page == "Exercise Library":
        show_library()
    elif page == "AI Coach Chat":
        show_ai_coach()
    elif page == "My Profile":
        show_profile()
    elif page == "Settings":
        show_settings()


if __name__ == "__main__":
    main()
