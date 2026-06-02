import streamlit as st


def show_library():
    """
    Renders the reference library for the 5 exercises supported by RepSense.
    """
    st.markdown("<h1 style='color: #ffffff;'>📖 Exercise Reference Library</h1>", unsafe_allow_html=True)
    st.write("Understand correct setups, target muscle groups, and what posture indicators the AI model monitors.")

    # 1. Selection tab for clean categorization
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏋️ Bicep Curls", 
        "🍑 Squats", 
        "🤸 Pushups", 
        "🦵 Lunges", 
        "💪 Shoulder Press"
    ])

    with tab1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Dumbbell / Barbell Bicep Curls")
        st.write("**Target Muscles:** Biceps Brachii, Brachialis, Brachioradialis")
        st.write("---")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🎯 Execution Setup")
            st.write("- Stand tall with feet shoulder-width apart, holding weights at your sides.")
            st.write("- Keep your elbows close to your torso with palms facing forward.")
            st.write("- Curl the weights while contracting your biceps; keep wrists straight.")
            st.write("- Lower the weights back under control to the start position.")
        with col_r:
            st.markdown("#### 🤖 AI Form Checks")
            st.write("❌ **Elbow Drift:** Raising elbows forward shifts the load to front deltoids. Keep elbow joints pinned.")
            st.write("❌ **Body Swing:** Leaning back and rocking the torso to swing the weight. Keep core braced.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Bodyweight / Weighted Squats")
        st.write("**Target Muscles:** Quadriceps, Gluteus Maximus, Hamstrings, Core")
        st.write("---")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🎯 Execution Setup")
            st.write("- Stance shoulder-width apart, toes pointing slightly outward.")
            st.write("- Lower your hips back and down as if sitting in an imaginary chair.")
            st.write("- Keep your chest upright and head forward.")
            st.write("- Stand back up by pushing through your heels, fully extending hips at the top.")
        with col_r:
            st.markdown("#### 🤖 AI Form Checks")
            st.write("❌ **Improper Depth:** Stopping before thighs are parallel to the floor (knee angle below 100 degrees).")
            st.write("❌ **Forward Lean:** Letting the torso collapse forward, putting stress on the lower spine. Keep chest up.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Classic Floor Pushups")
        st.write("**Target Muscles:** Pectoralis Major, Triceps Brachii, Anterior Deltoids, Core")
        st.write("---")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🎯 Execution Setup")
            st.write("- Place hands slightly wider than shoulder-width on the floor.")
            st.write("- Position feet together, locking knees and engaging glutes.")
            st.write("- Lower your body until your chest nearly touches the floor; keep elbows at a 45-degree angle.")
            st.write("- Press back up to full elbow extension.")
        with col_r:
            st.markdown("#### 🤖 AI Form Checks")
            st.write("❌ **Hip Sagging:** Lower back arching and hips dropping. Indicates weak core activation.")
            st.write("❌ **Hip Piking:** Hips pushing upward in a bent triangle. Shifts load off chest to shoulders.")
            st.write("❌ **Bent Spine:** Not moving the chest and hips together as a single rigid plank.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Alternating Forward Lunges")
        st.write("**Target Muscles:** Quadriceps, Glutes, Hamstrings, Calves")
        st.write("---")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🎯 Execution Setup")
            st.write("- Stand tall, feet hip-width apart.")
            st.write("- Take a large step forward, keeping your torso upright.")
            st.write("- Lower your body until your back knee is just above the floor and front thigh is parallel.")
            st.write("- Push off your front foot to return to the starting posture.")
        with col_r:
            st.markdown("#### 🤖 AI Form Checks")
            st.write("❌ **Front Knee Flare:** Letting the front knee cave in or extend past the toes.")
            st.write("❌ **Loss of Balance:** Torso shifting side to side. Keep weight centered over the hips.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab5:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Dumbbell / Barbell Overhead Shoulder Press")
        st.write("**Target Muscles:** Deltoids (Anterior & Lateral), Triceps Brachii, Upper Pectorals")
        st.write("---")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🎯 Execution Setup")
            st.write("- Hold weights at shoulder height with elbows bent directly underneath.")
            st.write("- Stand tall, engage glutes and brace your core.")
            st.write("- Press the weights straight overhead until arms are fully locked out.")
            st.write("- Control the weight back down to shoulder level.")
        with col_r:
            st.markdown("#### 🤖 AI Form Checks")
            st.write("❌ **Partial Range of Motion:** Not extending elbows fully overhead at the top.")
            st.write("❌ **Lower Back Arch:** Leaning backward to press weight. Indicates hyper-extended lumbar spine.")
        st.markdown("</div>", unsafe_allow_html=True)
