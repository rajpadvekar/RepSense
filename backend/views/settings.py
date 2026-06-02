import os
import streamlit as st
from database.db_manager import DBManager


def show_settings():
    """
    Renders the app settings page. Allows configuring API overrides
    and clearing database workout logs.
    """
    user = st.session_state.user

    st.markdown("<h1 style='color: #ffffff;'>⚙️ System Settings</h1>", unsafe_allow_html=True)
    st.write("Manage your integration keys, camera choices, and local profile configurations.")

    # 1. API Configuration
    st.markdown("<div class='glass-card glow-card'>", unsafe_allow_html=True)
    st.markdown("### 🔑 API Integrations")
    st.write("")
    
    # Check if a default exists in the environment
    env_groq_key = os.environ.get("GROQ_API_KEY", "")
    current_override = st.session_state.get("groq_api_key_override", "")

    display_key = current_override or (env_groq_key[:10] + "..." if env_groq_key else "")
    
    new_override = st.text_input(
        "Groq API Key Override",
        type="password",
        placeholder="Paste your Groq gsk_ API key here...",
        help="If left blank, RepSense will use the .env key or fallback to offline rule-based coaching."
    )
    
    if st.button("Save API Configuration", key="save_api_settings_btn"):
        if new_override.strip():
            st.session_state.groq_api_key_override = new_override.strip()
            st.success("Custom Groq API Key saved successfully for this session!")
        else:
            st.session_state.groq_api_key_override = ""
            st.success("Resetting to default environment variable settings.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Database cleanup
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### ⚠️ Account Data Management")
    st.write("This action is irreversible. All workout logs and postural history for your account will be cleared.")
    st.write("")
    
    confirm_clear = st.checkbox("I understand that clearing my logs cannot be undone.", value=False, key="confirm_clear_checkbox")
    
    if st.button("Clear Workout History", key="clear_history_btn"):
        if not confirm_clear:
            st.warning("Please check the confirmation box before clearing your training logs.")
        else:
            try:
                # Remove workout logs for this user (which will cascade-delete feedback logs via foreign key constraint)
                with DBManager.get_connection() as conn:
                    conn.execute("DELETE FROM workouts WHERE user_id = ?", (user["id"],))
                    conn.commit()
                st.success("Your workout history logs have been cleared successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing workout database logs: {e}")
                
    st.markdown("</div>", unsafe_allow_html=True)
