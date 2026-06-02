import streamlit as st
from services.auth_service import AuthService


def show_profile():
    """
    Renders the profile view where the user can update height, weight,
    and daily fitness targets.
    """
    user = st.session_state.user
    
    # Reload profile values from database to ensure fresh fields
    profile = AuthService.get_profile(user["id"])
    if not profile:
        profile = user

    st.markdown("<h1 style='color: #ffffff;'>👤 My Profile & Goals</h1>", unsafe_allow_html=True)
    st.write("Manage your physical biometric info and adjust daily training goals.")

    col_form, col_info = st.columns([1.5, 1])

    with col_form:
        st.markdown("<div class='glass-card glow-card'>", unsafe_allow_html=True)
        st.markdown("### ⚙️ Biometrics & Stargets")
        st.write("")
        
        # Load fields, handling default null values
        current_height = profile.get("height") or 175.0
        current_weight = profile.get("weight") or 70.0
        current_goal = profile.get("daily_rep_goal") or 50

        # Form fields
        new_height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=float(current_height), step=0.5)
        new_weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=float(current_weight), step=0.5)
        new_goal = st.number_input("Daily Reps Target", min_value=1, max_value=1000, value=int(current_goal), step=5)
        
        st.write("")
        if st.button("Update Profile Details", key="update_profile_btn"):
            success = AuthService.update_profile(
                user_id=profile["id"],
                height=new_height,
                weight=new_weight,
                daily_rep_goal=new_goal
            )
            if success:
                # Sync session states
                updated_user = AuthService.get_profile(profile["id"])
                st.session_state.user = updated_user
                st.success("Profile statistics updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update profile. Please verify your input parameters.")
                
        st.markdown("</div>", unsafe_allow_html=True)

    with col_info:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📋 Account Information")
        st.write("")
        st.write(f"👤 **Username:** {profile['username']}")
        st.write(f"📧 **Email:** {profile['email']}")
        st.write(f"📅 **Member Since:** {profile['created_at'].split(' ')[0] if ' ' in profile['created_at'] else profile['created_at']}")
        
        st.write("---")
        st.markdown("💡 **Why are these needed?**")
        st.markdown(
            "Your weight and height help the AI coach compute calorie burn estimates "
            "and suggest appropriate resting periods. Daily targets are displayed "
            "on the Home tracker."
        )
        st.markdown("</div>", unsafe_allow_html=True)
