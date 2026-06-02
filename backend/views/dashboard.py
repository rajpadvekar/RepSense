import streamlit as st
import pandas as pd
from services.workout_service import WorkoutService


def show_dashboard():
    """
    Displays the Analytics Dashboard containing statistics summaries,
    progress tracking graphs, and detailed workout history lists.
    """
    user = st.session_state.user
    
    st.markdown("<h1 style='color: #ffffff;'>📊 Workout Analytics & Dashboard</h1>", unsafe_allow_html=True)
    st.write("Review your historical logs, performance scores, and training consistency details below.")

    # Retrieve stats data from services
    analytics = WorkoutService.get_dashboard_analytics(user["id"])
    history = WorkoutService.get_workout_history(user["id"])

    if not history:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.info("No workout sessions logged yet! Complete a set on the 'Live Workout' page to see your analytics.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # 1. Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.metric(label="Total Workouts", value=analytics["total_sessions"])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.metric(label="Total Reps", value=analytics["total_reps"])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.metric(label="Overall Avg Form", value=f"{analytics['overall_avg_score']}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col4:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.metric(label="Total Minutes", value=analytics["total_duration_minutes"])
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. Convert history to Pandas DataFrame for analysis
    df = pd.DataFrame(history)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["date_label"] = df["created_at"].dt.strftime("%b %d, %Y")

    # Layout for charts
    c_left, c_right = st.columns([1.5, 1])

    with c_left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📈 Reps Trend Over Time")
        
        # Aggregate reps by date to show training progression
        trend_df = df.groupby("date_label", sort=False)["reps"].sum().reset_index()
        st.line_chart(trend_df, x="date_label", y="reps", color="#f5a623")
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🏋️ Exercise Breakdown")
        
        # Aggregate reps and count by exercise
        breakdown_df = df.groupby("exercise_name")["reps"].sum().reset_index()
        st.bar_chart(breakdown_df, x="exercise_name", y="reps", color="#00d4ff")
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Workout History Logs Details
    st.markdown("### 📂 Detailed Workout Logs")
    
    for _, row in df.iterrows():
        # Create expandable rows for each workout session
        session_id = row["id"]
        exercise_name = row["exercise_name"]
        reps = row["reps"]
        avg_score = row["avg_form_score"]
        duration_mins = round(row["duration_seconds"] / 60.0, 1)
        timestamp = row["date_label"]

        # Fetch feedback details logged for this session
        feedbacks = WorkoutService.get_workout_feedbacks(session_id)

        # Style header summary for the log item
        header_title = f"🗓️ {timestamp} — {exercise_name} | {reps} Reps | Form: {avg_score}% ({duration_mins} min)"
        
        with st.expander(header_title):
            st.write(f"**Session ID:** {session_id}")
            st.write(f"**Duration:** {row['duration_seconds']} seconds")
            st.write(f"**Average Form score:** {avg_score}%")
            
            st.write("**Specific Posture Feedbacks Logged:**")
            if feedbacks:
                for idx, f_text in enumerate(feedbacks, 1):
                    st.write(f"{idx}. {f_text}")
            else:
                st.write("✨ Clean session! No posture errors detected by AI.")
