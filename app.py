import streamlit as st
import random, csv, os
from datetime import datetime
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Page Setup
# --------------------------------------------------
st.set_page_config(page_title="AI Creativity and Idea Generation Survey", layout="wide")
st.title("🧠 AI Creativity and Idea Generation Survey")

# --------------------------------------------------
# Initialize Session
# --------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "intro"
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "text_round" not in st.session_state:
    st.session_state.text_round = 0
if "category_order" not in st.session_state:
    st.session_state.category_order = []

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def save_response(data):
    file_exists = os.path.isfile("responses.csv")
    with open("responses.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def load_responses():
    if os.path.exists("responses.csv"):
        return pd.read_csv("responses.csv")
    return pd.DataFrame()

# --------------------------------------------------
# Intro
# --------------------------------------------------
if st.session_state.page == "intro":
    st.markdown("""
    Welcome!  
    This study explores how people create text and image captions with or without AI help.  
    Your answers are anonymous, and you may stop anytime.
    """)
    if st.button("Start Survey"):
        st.session_state.page = "demographics"
        st.rerun()

# --------------------------------------------------
# A. Participant Info
# --------------------------------------------------
elif st.session_state.page == "demographics":
    st.header("A. Participant Information")
    pid = st.text_input("Participant ID (create any short code)")
    age = st.text_input("Age")
    gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Other"])
    major = st.text_input("Major or academic background")
    language = st.text_input("Native language (optional)")
    creative = st.text_area("Describe any prior creative work (writing, design, etc.)")

    if st.button("Next ➡️"):
        st.session_state.responses.update({
            "participant_id": pid,
            "age": age,
            "gender": gender,
            "major": major,
            "language": language,
            "creative_exp": creative,
            "timestamp_start": datetime.now().isoformat()
        })
        st.session_state.page = "ai_familiarity"
        st.rerun()

# --------------------------------------------------
# B. AI Familiarity
# --------------------------------------------------
elif st.session_state.page == "ai_familiarity":
    st.header("B. AI Familiarity and Usage (1–5 scale)")
    likerts = {}
    qs = [
        "I regularly use AI tools (ChatGPT, Grammarly, etc.) for creative or academic work.",
        "I feel confident evaluating AI-generated outputs.",
        "I find AI tools helpful for improving my writing or design ideas.",
        "I rely on AI suggestions more than my own ideas.",
        "I trust AI systems to provide unbiased suggestions."
    ]
    for i, q in enumerate(qs):
        likerts[q] = st.slider(q, 1, 5, 3, key=f"ai_fam_{i}")

    if st.button("Next ➡️"):
        st.session_state.responses.update(likerts)
        st.session_state.page = "text_tasks"
        st.category_order = []
        st.text_round = 0
        st.rerun()

# --------------------------------------------------
# C. Text Generation (3 rounds randomized)
# --------------------------------------------------
elif st.session_state.page == "text_tasks":
    st.header("C. Text Generation: Write Headlines")

    # Define briefs
    briefs = {
        "Science & Technology": {
            "brief": "Researchers developed a new EV battery that charges in under five minutes, promising to revolutionize electric mobility.",
            "ai": [
                "Breakthrough Battery Promises Ultra-Fast EV Charging",
                "Rapid-Charge EV Battery Could Transform Electric Mobility",
                "University Team Unveils Lightning-Fast EV Battery Tech"
            ]
        },
        "Culture & Sports": {
            "brief": "A small rural town is hosting an international chess festival with players from 40 countries, bringing new life and pride to the community.",
            "ai": [
                "Global Chess Festival Brings New Life to Rural Town",
                "Quiet Town Turns Global Hub for Chess Enthusiasts",
                "From Silence to Strategy: Chess Festival Transforms Local Community"
            ]
        },
        "Health & Wellness": {
            "brief": "A new app claims it can detect stress by analyzing your voice. Developers say it can help track mental health in real time.",
            "ai": [
                "AI Listens for Stress: App Tracks Mental Health Through Speech",
                "Can Your Voice Reveal Stress? New AI App Says Yes",
                "Smartphone App Uses AI to Measure Stress in Real Time"
            ]
        }
    }

    # Randomize categories once
    if not st.session_state.category_order:
        st.session_state.category_order = random.sample(list(briefs.keys()), 3)

    categories = st.session_state.category_order
    round_idx = st.session_state.text_round
    round_conditions = ["No-AI", "AI-first", "Human-first"]

    if round_idx < 3:
        current_category = categories[round_idx]
        condition = round_conditions[round_idx]
        content = briefs[current_category]
        st.subheader(f"Round {round_idx+1}: {current_category}")
        st.write("**Brief:**", content["brief"])
        user_key = f"{current_category}_response"

        if condition == "No-AI":
            st.markdown("_Please write your own headlines for this brief._")
            user_text = st.text_area("Write 3–5 headlines:", key=f"{current_category}_text")
            st.session_state.responses[user_key] = user_text
            if user_text.strip() and st.button("Next ➡️"):
                st.session_state.text_round += 1
                st.rerun()
            elif not user_text.strip():
                st.info("✏️ Please enter your headlines before proceeding.")

        elif condition == "AI-first":
            st.markdown("### Example AI Headlines")
            for h in content["ai"]:
                st.write("-", h)
            st.markdown("_Now write your own headlines inspired by the above._")
            user_text = st.text_area("Write 3–5 headlines:", key=f"{current_category}_text")
            st.session_state.responses[user_key] = user_text
            if user_text.strip() and st.button("Next ➡️"):
                st.session_state.text_round += 1
                st.rerun()
            elif not user_text.strip():
                st.info("✏️ Please enter your headlines before proceeding.")

        else:  # Human-first
            st.markdown("_Please write your own headlines first._")
            user_text = st.text_area("Write 3–5 headlines:", key=f"{current_category}_text")

            # Reveal AI suggestions only after input
            if user_text.strip():
                st.markdown("### Example AI Headlines")
                for h in content["ai"]:
                    st.write("-", h)
                st.markdown("_You may revise your ideas after viewing the AI examples._")

            st.session_state.responses[user_key] = user_text
            if user_text.strip() and st.button("Next ➡️"):
                st.session_state.text_round += 1
                st.rerun()
            elif not user_text.strip():
                st.info("✏️ Please enter your headlines before proceeding.")

    else:
        st.subheader("Post-Survey: Reflect on the Text Generation Task")
        st.markdown("Rate your overall experience across all three rounds (1–5):")
        st.session_state.responses["overall_trust"] = st.slider("Overall, I trusted the AI suggestions.", 1, 5, 3)
        st.session_state.responses["overall_original"] = st.slider("Overall, my ideas felt original.", 1, 5, 3)
        st.session_state.responses["overall_fixation"] = st.slider("It was hard to think beyond the AI’s ideas.", 1, 5, 3)
        if st.button("Next ➡️"):
            st.session_state.page = "image_tasks"
            st.rerun()

# --------------------------------------------------
# D. Image Caption Tasks
# --------------------------------------------------
elif st.session_state.page == "image_tasks":
    st.header("D. Image Caption Tasks")

    image_sets = [
        ("image1.jpg", "Cooking caption ideas", [
            "Taste-testing: the most important step in every masterpiece.",
            "Cooking is an art — tasting is quality control.",
            "When in doubt, taste it out."
        ]),
        ("image2.jpg", "1920s party scene captions", [
            "When the champagne hits before the Roaring Twenties end.",
            "Pour decisions make the best memories."
        ]),
        ("image3.jpg", "Photographers with cameras captions", [
            "Smile! You’re making tomorrow’s headlines.",
            "Before smartphones, there were these warriors of the lens."
        ]),
        ("image4.jpg", "3D movie reaction captions", [
            "When 3D movies were too real.",
            "Immersive cinema before VR was even a dream."
        ]),
        ("image5.jpg", "Bubble party captions", [
            "When the bubble gun steals the show.",
            "POV: The party just hit its peak."
        ]),
        ("image6.jpg", "Mountain hiking captions", [
            "Every trail leads to a story worth telling.",
            "Adventure begins at the edge of your comfort zone."
        ]),
        ("image7.jpg", "Brainstorming teamwork captions", [
            "Collaboration in action: where ideas come alive in color.",
            "Teamwork is the art of turning many thoughts into one vision."
        ]),
        ("image8.jpg", "Funny science classroom captions", [
            "When your financial plan is pure wizardry.",
            "Inflation, but make it magical."
        ])
    ]

    cond = random.choice(["AI-first", "Human-first", "No-AI"])  # Random per participant
    for img, name, ais in image_sets:
        st.subheader(name)
        image_path = Path(__file__).parent / img
        if image_path.exists():
            st.image(str(image_path), caption=f"{name}")
        else:
            st.warning(f"⚠️ Could not find {img}. Please verify filename.")

        if cond == "AI-first":
            st.markdown("### Example AI Captions")
            for c in ais:
                st.write("-", c)
            st.session_state.responses[f"{img}_caption"] = st.text_area("Write your own caption(s):", key=f"{img}_text")
        elif cond == "Human-first":
            cap = st.text_area("Write your own caption(s):", key=f"{img}_text")
            st.markdown("### Example AI Captions")
            for c in ais:
                st.write("-", c)
            st.session_state.responses[f"{img}_caption"] = cap
        else:
            st.session_state.responses[f"{img}_caption"] = st.text_area("Write your own caption(s):", key=f"{img}_text")

        st.session_state.responses[f"{img}_trust"] = st.slider(
            "I trusted the AI suggestions.", 1, 5, 3, key=f"{img}_trust_slider"
        )
        st.session_state.responses[f"{img}_original"] = st.slider(
            "My ideas felt original.", 1, 5, 3, key=f"{img}_orig_slider"
        )
        st.session_state.responses[f"{img}_fixation"] = st.slider(
            "It was hard to think beyond the AI’s ideas.", 1, 5, 3, key=f"{img}_fix_slider"
        )

    if st.button("Finish Survey ✅"):
        st.session_state.responses["timestamp_end"] = datetime.now().isoformat()
        save_response(st.session_state.responses)
        st.session_state.page = "done"
        st.rerun()

# --------------------------------------------------
# End Page
# --------------------------------------------------
elif st.session_state.page == "done":
    st.balloons()
    st.header("✅ Survey Complete")
    st.success("Thank you! Your responses have been saved.")

    st.markdown("### 📊 Download All Responses")
    df = load_responses()
    if len(df) > 0:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download responses.csv",
            data=csv_data,
            file_name="responses.csv",
            mime="text/csv"
        )
    else:
        st.info("No responses recorded yet.")
