import streamlit as st
import os
from services.ai_coach_service import AICoachService


def show_planner():
    """
    Renders the Workout & Diet Planner page, generating plans dynamically
    via the Groq AI service or rendering tailored offline templates.
    """
    user = st.session_state.user
    
    st.markdown("<h1 style='color: #ffffff;'>📋 AI Workout & Diet Planner</h1>", unsafe_allow_html=True)
    st.write("Generate personalized nutrition charts and custom exercise schedules tailored to your fitness objectives.")

    st.markdown("<div class='glass-card glow-card'>", unsafe_allow_html=True)
    
    col_g, col_d = st.columns(2)
    with col_g:
        goal = st.selectbox(
            "YOUR FITNESS GOAL",
            ["Muscle Gain (Hypertrophy)", "Fat Loss (Caloric Deficit)", "Lean & Tone (Body Recomp)", "Endurance & Stamina"]
        )
    with col_d:
        diet_type = st.selectbox(
            "DIETARY PREFERENCE",
            ["Vegetarian", "Vegan", "Non-Vegetarian", "Keto / Low-Carb"]
        )

    # Biometric info summary for contextual prompt inputs
    height = user.get("height") or 175.0
    weight = user.get("weight") or 70.0

    st.write("")
    generate_clicked = st.button("Generate My Personalized Plans", key="generate_plans_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    if generate_clicked:
        # Prompt build
        prompt = (
            f"Generate a customized, highly structured 1-week workout plan and a corresponding daily diet plan. "
            f"The user's goal is '{goal}'. "
            f"Dietary preference: '{diet_type}'. "
            f"User profile details: Height: {height} cm, Weight: {weight} kg. "
            f"Please divide your response into two distinct sections: "
            f"1. WORKOUT SCHEDULE (day-by-day routines including squats, pushups, bicep curls, etc.) "
            f"2. DIET & MEAL PLAN (breakfast, lunch, snack, dinner suggestions with target macros)."
        )

        with st.spinner("Analyzing metrics and compiling plans..."):
            api_key_override = st.session_state.get("groq_api_key_override")
            client = AICoachService.get_groq_client(api_key_override)
            
            if client:
                try:
                    # Request dynamic response from Groq LLM
                    response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are a professional fitness planner and sports dietitian. Provide clean, well-formatted markdown plans."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=800,
                        temperature=0.7
                    )
                    plan_text = response.choices[0].message.content
                    
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.markdown(plan_text)
                    st.markdown("</div>", unsafe_allow_html=True)
                    return
                except Exception as e:
                    print(f"Planner API Error: {e}")

            # --- Fallback offline plans ---
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.info("Using offline plan templates. Connect a GROQ_API_KEY in Settings to customize dynamically.")
            
            if "Muscle" in goal:
                st.markdown(
                    "### 💪 1-Week Muscle Gain Schedule\n"
                    "* **Mon / Thu (Upper Body Focus):** Bicep curls (4 sets of 12 reps), Shoulder Press (4 sets of 10 reps), Pushups (4 sets to failure).\n"
                    "* **Tue / Fri (Lower Body Focus):** Squats (4 sets of 15 reps), Lunges (4 sets of 12 reps each leg), Calf raises.\n"
                    "* **Wed / Sat / Sun:** Rest & core recovery active stretches.\n\n"
                    f"### 🥦 Daily {diet_type} Hypertrophy Diet Plan\n"
                    "* **Breakfast:** High-protein oatmeal topped with nut butter and fruit, or scrambled eggs/tofu.\n"
                    "* **Lunch:** Brown rice with beans/lentils (vegetarian) or chicken breast (non-vegetarian) and mixed green salad.\n"
                    "* **Snack:** Greek yogurt (or soy yogurt) with whey protein powder and mixed berries.\n"
                    "* **Dinner:** Quinoa stir-fry with baked tofu, edamame, and broccoli, served with avocado dressing."
                )
            elif "Fat" in goal:
                st.markdown(
                    "### 🏃 1-Week Fat Loss Schedule\n"
                    "* **Mon / Wed / Fri (Full Body Circuit):** Squats (3 sets of 20 reps), Pushups (3 sets of 15 reps), Lunges (3 sets of 15 reps).\n"
                    "* **Tue / Thu (HIIT):** 20 minutes active interval sprints, jump ropes, and light bicep curls.\n"
                    "* **Sat / Sun:** Active recovery walks.\n\n"
                    f"### 🥗 Daily {diet_type} Deficit Diet Plan\n"
                    "* **Breakfast:** Spinach and berry green smoothie mixed with plant protein powder.\n"
                    "* **Lunch:** Large green salad topped with steamed lentils, chia seeds, and light olive oil dressing.\n"
                    "* **Snack:** Handful of almonds and 1 apple.\n"
                    "* **Dinner:** Grilled salmon (non-vegetarian) or roasted chickpeas (vegetarian) with steamed asparagus and cauliflower rice."
                )
            else:
                st.markdown(
                    "### 🏋️ 1-Week Body Recomp Schedule\n"
                    "* **Mon / Wed / Fri (Full Body Strength):** Squats (3 sets of 12 reps), Pushups (3 sets of 12 reps), Shoulder Press (3 sets of 12 reps).\n"
                    "* **Tue / Thu (Active Recovery):** Yoga, stretching, light walks.\n"
                    "* **Sat / Sun:** Rest.\n\n"
                    f"### 🍱 Daily {diet_type} Macro Balanced Diet Plan\n"
                    "* **Breakfast:** Avocado toast topped with poached eggs (non-vegetarian) or tofu scramble (vegan).\n"
                    "* **Lunch:** Whole wheat wrap loaded with hummus, spinach, falafel, and cucumbers.\n"
                    "* **Snack:** Protein bar and a banana.\n"
                    "* **Dinner:** Grilled chicken breast/tempeh served with sweet potato wedges and steamed green beans."
                )
            st.markdown("</div>", unsafe_allow_html=True)
