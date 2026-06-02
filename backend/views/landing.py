import streamlit as st
from services.workout_service import WorkoutService


def show_landing():
    """
    Renders the beautiful landing and welcome page inside the application.
    """
    user = st.session_state.user

    # Welcome header banner
    st.markdown(
        f"<h1 style='color: #ffffff;'>Welcome, {user['username']}! 🦾</h1>"
        f"<p style='color: #888888; font-size: 16px; margin-bottom: 30px;'>RepSense handles your posture checking in real-time so you can focus on building strength.</p>",
        unsafe_allow_html=True
    )

    # Fetch simple user statistics for progress greeting
    stats = WorkoutService.get_dashboard_analytics(user["id"])
    daily_goal = user.get("daily_rep_goal", 50)
    progress_pct = min(100, int((stats["today_reps"] / daily_goal) * 100)) if daily_goal > 0 else 100

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='glass-card glow-card'>", unsafe_allow_html=True)
        st.markdown("### 🚀 Quick Start Guide")
        st.write("")
        st.write("1. **Go to Live Workout:** Select 'Live Workout' on the sidebar.")
        st.write("2. **Configure Camera:** Grant webcam permission when prompted by your browser.")
        st.write("3. **Choose Exercise:** Select squats, pushups, curls, lunges, or overhead presses.")
        st.write("4. **Listen for Feedback:** Keep your volume up! The AI Coach speaks out corrections in real-time.")
        st.write("5. **Log Session:** When finished, click 'Finish & Log Workout' to save your statistics.")
        
        st.write("")
        st.markdown("</div>", unsafe_allow_html=True)

        # Highlight feature cards
        st.markdown("### 🌟 AI Coaching Capabilities")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                "<div class='glass-card'>"
                "<h4>🤖 Form Analysis HUD</h4>"
                "<p style='color: #888888; font-size: 13px;'>Detects posture errors like sagging hips in pushups, elbow drift in curls, and improper depth in squats in real-time.</p>"
                "</div>",
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                "<div class='glass-card'>"
                "<h4>🔊 Spoken Corrections</h4>"
                "<p style='color: #888888; font-size: 13px;'>Uses text-to-speech feedback to instantly read out adjustments, acting as a personal trainer in your room.</p>"
                "</div>",
                unsafe_allow_html=True
            )
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📅 Today's Progress")
        st.write("")
        
        st.metric(label="Reps Completed Today", value=f"{stats['today_reps']} / {daily_goal}")
        st.progress(progress_pct / 100.0)
        st.write(f"**{progress_pct}%** of your daily rep target achieved.")

        st.write("---")
        st.markdown("#### Overall Stats")
        st.write(f"🏋️ **Sessions Logged:** {stats['total_sessions']}")
        st.write(f"🔄 **Total Reps:** {stats['total_reps']}")
        st.write(f"🎯 **Avg Form Score:** {stats['overall_avg_score']}%")
        st.write(f"⏱️ **Time Trained:** {stats['total_duration_minutes']} mins")
        st.markdown("</div>", unsafe_allow_html=True)
