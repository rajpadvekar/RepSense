import streamlit as st
from services.ai_coach_service import AICoachService
from services.workout_service import WorkoutService


def show_ai_coach():
    """
    Renders the interactive AI Coach Chat interface, connecting to the Groq LLM.
    Generates text and optional audio responses in real-time.
    """
    user = st.session_state.user

    st.markdown("<h1 style='color: #ffffff;'>🤖 AI Trainer & Coach Chat</h1>", unsafe_allow_html=True)
    st.write("Ask RepSense Coach about exercise routines, form corrections, diet, or recovery.")

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": f"Hi {user['username']}! I am your virtual trainer. How can I help you crush your workout goals today?"
            }
        ]

    # Voice coach toggle for chat page
    voice_chat_enabled = st.checkbox("Read coach responses aloud 🔊", value=True, key="voice_chat_toggle")

    # Render previous messages from session state
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input box
    if user_prompt := st.chat_input("Ask a question (e.g., 'How do I stop my lower back from arching during shoulder press?')"):
        # 1. Display user input
        with st.chat_message("user"):
            st.write(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        # 2. Gather context from database stats
        stats = WorkoutService.get_dashboard_analytics(user["id"])
        workout_context = (
            f"User profile: height={user.get('height')}cm, weight={user.get('weight')}kg. "
            f"Logged sessions={stats['total_sessions']}, total reps={stats['total_reps']}, "
            f"overall average form score={stats['overall_avg_score']}%."
        )

        # 3. Request LLM response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*Coach is formulating advice...*")
            
            # Read key override from settings if any
            api_key_override = st.session_state.get("groq_api_key_override")
            
            coach_reply = AICoachService.ask_coach(
                user_message=user_prompt,
                chat_history=st.session_state.chat_history,
                workout_context=workout_context,
                api_key_override=api_key_override
            )
            
            message_placeholder.write(coach_reply)
            
        st.session_state.chat_history.append({"role": "assistant", "content": coach_reply})

        # 4. Speak response aloud if enabled
        if voice_chat_enabled:
            audio_bytes = AICoachService.generate_speech(coach_reply)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)

        # Rerun to sync chat bubbles
        st.rerun()
