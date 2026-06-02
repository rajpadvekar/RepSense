import time
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from core.video_processor import VideoProcessor
from services.ai_coach_service import AICoachService
from services.workout_service import WorkoutService

# Simple default STUN server configurations for WebRTC video connection
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


def show_live_workout():
    """
    Renders the live workout screen with real-time pose skeleton stream,
    HUD readout updates, text-to-speech voice cueing, and log storage.
    """
    user = st.session_state.user

    st.markdown("<h1 style='color: #ffffff;'>🏋️ Live AI Workout Page</h1>", unsafe_allow_html=True)
    st.write("Position yourself so your full body (head to feet) is visible in the camera frame.")

    # 1. Selection options
    col_sel, col_goal, col_ctrl = st.columns([2, 1, 1])
    
    with col_sel:
        exercise = st.selectbox(
            "CHOOSE YOUR EXERCISE",
            ["Bicep Curls", "Squats", "Pushups", "Lunges", "Shoulder Press"],
            key="active_exercise_selectbox"
        )
        
    with col_goal:
        target_reps = st.number_input(
            "TARGET REPS GOAL 🎯",
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            key="target_reps_input"
        )
    
    with col_ctrl:
        st.write("")
        voice_enabled = st.checkbox("Enable Audio Voice Coach 🔊", value=True, key="voice_coach_toggle")

    # Keep track of workout timing
    if "workout_start_time" not in st.session_state:
        st.session_state.workout_start_time = None
    if "last_spoken_feedback" not in st.session_state:
        st.session_state.last_spoken_feedback = ""
    if "accumulated_scores" not in st.session_state:
        st.session_state.accumulated_scores = []
    if "logged_feedbacks" not in st.session_state:
        st.session_state.logged_feedbacks = set()

    # 2. Camera video streaming module
    webrtc_ctx = webrtc_streamer(
        key="pose-processing-streamer",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    # Initialize/switch exercise on the processor thread
    if webrtc_ctx.video_processor:
        webrtc_ctx.video_processor.set_exercise(exercise)
        if st.session_state.workout_start_time is None:
            st.session_state.workout_start_time = time.time()
            st.session_state.accumulated_scores = []
            st.session_state.logged_feedbacks = set()

    # Placeholders for live status readouts
    metrics_placeholder = st.empty()
    audio_placeholder = st.empty()
    actions_placeholder = st.empty()

    # Stats variables to log
    reps_completed = 0
    final_form_score = 100

    # 3. Dynamic polling loop during live video play
    if webrtc_ctx.state.playing:
        if webrtc_ctx.video_processor:
            stats = webrtc_ctx.video_processor.get_stats()
            reps_completed = stats["reps"]
            final_form_score = stats["form_score"]
            feedback = stats["feedback"]
            
            # Accumulate scores for average reporting
            st.session_state.accumulated_scores.append(final_form_score)
            if feedback and feedback != "Ready! Start your first rep.":
                st.session_state.logged_feedbacks.add(feedback)

            # Renders live values layout
            with metrics_placeholder.container():
                st.markdown("<div class='glass-card glow-card'>", unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                
                m1.metric(label="Reps Counted", value=reps_completed)
                m2.metric(label="Current Form Accuracy", value=f"{final_form_score}%")
                
                # Dynamic style box for feedback prompt
                color_alert = "#f5a623" if "!" in feedback or "Keep" not in feedback else "#00d4ff"
                m3.markdown(
                    f"<p style='font-size: 11px; color: #888888; text-transform: uppercase; margin-bottom: 2px;'>Coach Insight</p>"
                    f"<h4 style='color: {color_alert}; margin-top: 0px;'>{feedback}</h4>", 
                    unsafe_allow_html=True
                )
                st.markdown("</div>", unsafe_allow_html=True)

            # 4. Check if Target Reps goal has been achieved to Auto-Finish
            if reps_completed >= target_reps:
                duration = 0
                if st.session_state.workout_start_time:
                    duration = int(time.time() - st.session_state.workout_start_time)
                
                # Compute average form score
                avg_score = 100.0
                if st.session_state.accumulated_scores:
                    avg_score = sum(st.session_state.accumulated_scores) / len(st.session_state.accumulated_scores)
                
                # Store session record in Database
                workout_id = WorkoutService.log_workout(
                    user_id=user["id"],
                    exercise_name=exercise,
                    reps=reps_completed,
                    avg_form_score=round(avg_score, 1),
                    duration_seconds=duration,
                    feedback_list=list(st.session_state.logged_feedbacks)
                )
                
                if workout_id:
                    with metrics_placeholder.container():
                        st.markdown("<div class='glass-card glow-card'>", unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        m1.metric(label="Reps Counted", value=reps_completed)
                        m2.metric(label="Current Form Accuracy", value=f"{final_form_score}%")
                        m3.markdown(
                            f"<p style='font-size: 11px; color: #888888; text-transform: uppercase; margin-bottom: 2px;'>Coach Insight</p>"
                            f"<h4 style='color: #00ff00; margin-top: 0px;'>TARGET REACHED! 🎉</h4>", 
                            unsafe_allow_html=True
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    st.success(f"🎯 Target of {target_reps} reps reached! Set completed and logged automatically.")
                    
                    # Play voice cue "Workout completed!"
                    if voice_enabled:
                        audio_bytes = AICoachService.generate_speech(f"Excellent job! You have completed your set of {target_reps} {exercise}!")
                        if audio_bytes:
                            with audio_placeholder.container():
                                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    
                    # Reset tracking states
                    st.session_state.workout_start_time = None
                    st.session_state.accumulated_scores = []
                    st.session_state.logged_feedbacks = set()
                    webrtc_ctx.video_processor.reset_reps()
                    time.sleep(3)
                    st.rerun()

            # 5. Synthesize voice audio cues
            if voice_enabled and feedback and feedback != st.session_state.last_spoken_feedback:
                st.session_state.last_spoken_feedback = feedback
                # Skip speak on default idle instructions
                if "Adjust camera" not in feedback and "Ready" not in feedback:
                    audio_bytes = AICoachService.generate_speech(feedback)
                    if audio_bytes:
                        with audio_placeholder.container():
                            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

            # 6. Logs operations buttons
            with actions_placeholder.container():
                col_reset, col_log = st.columns(2)
                
                if col_reset.button("🔄 Reset Counter", key="reset_reps_btn"):
                    webrtc_ctx.video_processor.reset_reps()
                    st.session_state.accumulated_scores = []
                    st.session_state.logged_feedbacks = set()
                    st.success("Rep counter reset successfully.")
                
                if col_log.button("💾 Finish & Save Workout", key="log_workout_btn"):
                    duration = 0
                    if st.session_state.workout_start_time:
                        duration = int(time.time() - st.session_state.workout_start_time)
                    
                    # Compute average form score
                    avg_score = 100.0
                    if st.session_state.accumulated_scores:
                        avg_score = sum(st.session_state.accumulated_scores) / len(st.session_state.accumulated_scores)
                    
                    # Store session record in Database
                    workout_id = WorkoutService.log_workout(
                        user_id=user["id"],
                        exercise_name=exercise,
                        reps=reps_completed,
                        avg_form_score=round(avg_score, 1),
                        duration_seconds=duration,
                        feedback_list=list(st.session_state.logged_feedbacks)
                    )
                    
                    if workout_id:
                        st.success(f"Log Saved! You completed {reps_completed} reps of {exercise} with an average form of {round(avg_score, 1)}%!")
                        # Reset tracking states
                        st.session_state.workout_start_time = None
                        st.session_state.accumulated_scores = []
                        st.session_state.logged_feedbacks = set()
                        webrtc_ctx.video_processor.reset_reps()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Error saving workout session. Please try again.")

            # Force brief delay to control thread load
            time.sleep(0.3)
            st.rerun()
    else:
        # Informative box displayed when camera feed is not running
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.info("Click the 'Start' button above to activate your webcam and load the AI Pose Pipeline.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Reset timing variable if camera stops
        st.session_state.workout_start_time = None
