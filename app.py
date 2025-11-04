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
if "condition_map" not in st.session_state:
    st.session_state.condition_map = []
if "image_round" not in st.session_state:
    st.session_state.image_round = 0
if "image_condition_map" not in st.session_state:
    st.session_state.image_condition_map = []

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
        st.text_round = 0
        st.condition_map = []
        st.rerun()

# --------------------------------------------------
# C. Text Generation (Counterbalanced)
# --------------------------------------------------
elif st.session_state.page == "text_tasks":
    st.header("C. Text Generation: Write Headlines")

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

    if not st.session_state.condition_map:
        topics = random.sample(list(briefs.keys()), 3)
        conditions = ["No-AI", "AI-first", "Human-first"]
        random.shuffle(conditions)
        st.session_state.condition_map = list(zip(conditions, topics))

    round_idx = st.session_state.text_round
    if round_idx < 3:
        condition, current_category = st.session_state.condition_map[round_idx]
        content = briefs[current_category]

        st.subheader(f"Round {round_idx + 1}: {current_category}")
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

            if user_text.strip():
                st.markdown("### Example AI Headlines")
                for h in content["ai"]:
                    st.write("-", h)
                st.markdown("**Do you think you could improve your ideas based on these AI examples?**")
                improve_choice = st.radio(
                    "Select one:", ["No", "Yes"],
                    index=0, horizontal=True, key=f"{current_category}_improve"
                )
                revised_text = ""
                if improve_choice == "Yes":
                    revised_text = st.text_area("Revise your headlines below:", key=f"{current_category}_revised")

                st.session_state.responses[user_key] = user_text
                st.session_state.responses[f"{current_category}_improved"] = improve_choice
                st.session_state.responses[f"{current_category}_revised_text"] = revised_text

                if st.button("Next ➡️"):
                    st.session_state.text_round += 1
                    st.rerun()
            else:
                st.info("✏️ Please enter your headlines before proceeding.")

    else:
        st.subheader("Post-Survey: Reflect on the Text Generation Task")
        st.markdown("Rate your overall experience across all three rounds (1–5):")
        st.session_state.responses["overall_trust"] = st.slider("Overall, I trusted the AI suggestions.", 1, 5, 3)
        st.session_state.responses["overall_original"] = st.slider("Overall, my ideas felt original.", 1, 5, 3)
        st.session_state.responses["overall_fixation"] = st.slider("It was hard to think beyond the AI’s ideas.", 1, 5, 3)
        if st.button("Next ➡️"):
            st.session_state.page = "image_tasks"
            st.image_round = 0
            st.image_condition_map = []
            st.rerun()

# --------------------------------------------------
# D. Image Caption Tasks (2 images × 3 rounds)
# --------------------------------------------------
elif st.session_state.page == "image_tasks":
    st.header("D. Image Caption Tasks")

    all_images = [
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

    # Create counterbalanced condition↔image pairs once
    if not st.session_state.image_condition_map:
        random.shuffle(all_images)
        image_pairs = [all_images[i:i+2] for i in range(0, 6, 2)]  # 3 rounds × 2 images
        conditions = ["No-AI", "AI-first", "Human-first"]
        random.shuffle(conditions)
        st.session_state.image_condition_map = list(zip(conditions, image_pairs))

    img_round = st.session_state.image_round
    if img_round < 3:
        condition, image_pair = st.session_state.image_condition_map[img_round]
        st.subheader(f"Round {img_round + 1}: Condition = {condition}")

        for img, name, ais in image_pair:
            st.markdown(f"### {name}")
            image_path = Path(__file__).parent / img
            if image_path.exists():
                st.image(str(image_path), caption=name)
            else:
                st.warning(f"⚠️ Could not find {img}.")

            # --- Condition logic ---
            if condition == "No-AI":
                cap = st.text_area("Write your own caption(s):", key=f"{img}_text")
            elif condition == "AI-first":
                st.markdown("**Example AI Captions**")
                for c in ais: st.write("-", c)
                cap = st.text_area("Write your own caption(s):", key=f"{img}_text")
            else:  # Human-first
                cap = st.text_area("Write your own caption(s):", key=f"{img}_text")
                if cap.strip():
                    st.markdown("**Example AI Captions**")
                    for c in ais: st.write("-", c)
                    st.markdown("**Could you improve your caption based on these AI examples?**")
                    improve_choice = st.radio("Select one:", ["No", "Yes"], index=0,
                                              horizontal=True, key=f"{img}_improve")
                    if improve_choice == "Yes":
                        cap += "\n[Revised] " + st.text_area("Revise your caption below:", key=f"{img}_revised")

            st.session_state.responses[f"{img}_caption"] = cap

        if st.button("Next ➡️"):
            st.session_state.image_round += 1
            st.rerun()

    else:
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
