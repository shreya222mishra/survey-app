import streamlit as st
import random, csv, os
from datetime import datetime
import pandas as pd
from pathlib import Path
from github import Github

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
    """Append a participant's responses safely, ensuring consistent column order."""
    df_new = pd.DataFrame([data])
    file_path = "responses.csv"

    if os.path.exists(file_path):
        try:
            df_existing = pd.read_csv(file_path)
            for col in df_existing.columns:
                if col not in df_new.columns:
                    df_new[col] = ""
            for col in df_new.columns:
                if col not in df_existing.columns:
                    df_existing[col] = ""
            df_new = df_new[df_existing.columns]
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
            df_final.to_csv(file_path, index=False, encoding="utf-8", quoting=csv.QUOTE_ALL)
        except Exception:
            backup_name = f"responses_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(file_path, backup_name)
            st.warning(f"⚠️ responses.csv corrupted — backed up as {backup_name}. A new file created.")
            df_new.to_csv(file_path, index=False, encoding="utf-8", quoting=csv.QUOTE_ALL)
    else:
        df_new.to_csv(file_path, index=False, encoding="utf-8", quoting=csv.QUOTE_ALL)


def load_responses():
    """Safely load previous responses; auto-backup if file is malformed."""
    file_path = "responses.csv"
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            backup_name = f"responses_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(file_path, backup_name)
            st.warning(f"⚠️ responses.csv was inconsistent and backed up as {backup_name}.")
            return pd.DataFrame()
    return pd.DataFrame()


def push_to_github(file_path):
    """Commit updated responses.csv to your GitHub repo."""
    try:
        token = st.secrets["github"]["token"]
        repo_name = st.secrets["github"]["repo"]
        g = Github(token)
        repo = g.get_repo(repo_name)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            file = repo.get_contents(file_path)
            repo.update_file(
                path=file_path,
                message=f"Update responses.csv - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                content=content,
                sha=file.sha
            )
        except Exception:
            repo.create_file(
                path=file_path,
                message=f"Add responses.csv - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                content=content
            )

        st.success("☁️ Data successfully backed up to GitHub repository.")
    except Exception as e:
        st.warning(f"⚠️ Backup to GitHub failed: {e}")

# --------------------------------------------------
# Intro
# --------------------------------------------------
if st.session_state.page == "intro":
    st.markdown("""
    Welcome!  
    This study explores how people create text and image captions with or without AI help.  
    Your answers are anonymous.
    """)
    if st.button("Start Survey"):
        st.session_state.page = "demographics"
        st.rerun()

# --------------------------------------------------
# A. Participant Info
# --------------------------------------------------
elif st.session_state.page == "demographics":
    st.header("A. Participant Information")
    pid = st.text_input("Participant ID (give your favourite number or short code)")
    age = st.text_input("Age")
    gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Other"])
    major = st.text_input("Major or academic background")

    if st.button("Next ➡️"):
        st.session_state.responses.update({
            "participant_id": pid,
            "age": age,
            "gender": gender,
            "major": major,
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
# C. Text Generation (Fixed Round Order, Shuffled Briefs)
# --------------------------------------------------
elif st.session_state.page == "text_tasks":
    st.header("C. Text Generation: Write Headlines")

    briefs = {
        "Science & Technology": {
            "brief": (
                "Researchers at a university lab have developed a new electric vehicle battery "
                "that can fully charge in under five minutes. The innovation could drastically "
                "reduce charging time and expand EV adoption worldwide. Automakers are already "
                "expressing interest in commercial trials."
            ),
            "ai": [
                "Breakthrough Battery Promises Ultra-Fast EV Charging",
                "Rapid-Charge EV Battery Could Transform Electric Mobility",
                "University Team Unveils Lightning-Fast EV Battery Tech"
            ]
        },
        "Culture & Sports": {
            "brief": (
                "A small rural town has become the global stage for an international chess festival. "
                "Players from over 40 countries are competing in local cafés, schools, and community centers. "
                "The event has brought tourism, media attention, and a new sense of pride to the community."
            ),
            "ai": [
                "Global Chess Festival Brings New Life to Rural Town",
                "Quiet Town Turns Global Hub for Chess Enthusiasts",
                "From Silence to Strategy: Chess Festival Transforms Local Community"
            ]
        },
        "Health & Wellness": {
            "brief": (
                "A new smartphone app claims it can detect a person’s stress levels simply by analyzing voice tone and pace. "
                "Developers say it could help users track mental health in real time. "
                "Experts are cautiously optimistic but warn about data privacy and accuracy concerns."
            ),
            "ai": [
                "AI Listens for Stress: App Tracks Mental Health Through Speech",
                "Can Your Voice Reveal Stress? New AI App Says Yes",
                "Smartphone App Uses AI to Measure Stress in Real Time"
            ]
        }
    }

    # Fixed round order: [No-AI, AI-first, Human-first], shuffled briefs
    if not st.session_state.condition_map:
        topics = random.sample(list(briefs.keys()), 3)
        st.session_state.condition_map = [
            ("No-AI", topics[0]),
            ("AI-first", topics[1]),
            ("Human-first", topics[2])
        ]

    round_idx = st.session_state.text_round
    if round_idx < 3:
        condition, current_category = st.session_state.condition_map[round_idx]
        content = briefs[current_category]
        base_key = condition.lower().replace("-", "_") + "_text"

        st.subheader(f"Round {round_idx + 1}: {current_category}")
        st.write("**Brief:**", content["brief"])
        st.session_state.responses[f"{base_key}_category"] = current_category

        if condition == "No-AI":
            st.markdown("_Compose a striking headline for this brief._")
            user_text = st.text_area("Write your headline:", key=f"text_{round_idx}")
            st.session_state.responses[base_key] = f"{current_category} — {user_text}"

        elif condition == "AI-first":
            st.markdown("### Example AI Headlines")
            for h in content["ai"]:
                st.write("-", h)
            st.markdown("_Now write your own headline inspired by the above._")
            user_text = st.text_area("Write your headline:", key=f"text_{round_idx}")
            st.session_state.responses[base_key] = f"{current_category} — {user_text}"

        else:  # Human-first
            st.markdown("_Write your headline first, then view AI examples._")
            user_text = st.text_area("Write your headline:", key=f"text_{round_idx}")
            st.session_state.responses[base_key] = f"{current_category} — {user_text}"

            if user_text.strip():
                st.markdown("### Example AI Headlines")
                for h in content["ai"]:
                    st.write("-", h)
                improve_choice = st.radio(
                    "Would you like to revise your headline based on these AI examples?",
                    ["No", "Yes"], index=0, horizontal=True, key=f"improve_{round_idx}"
                )
                revised_text = ""
                if improve_choice == "Yes":
                    revised_text = st.text_area("Revise your headline below:", key=f"revised_{round_idx}")
                st.session_state.responses[f"{base_key}_improved"] = improve_choice
                st.session_state.responses[f"{base_key}_revised"] = revised_text

        if user_text.strip() and st.button("Next ➡️"):
            st.session_state.text_round += 1
            st.rerun()

    else:
        st.session_state.page = "image_tasks"
        st.image_round = 0
        st.image_condition_map = []
        st.rerun()

# --------------------------------------------------
# D. Image Caption Tasks (Fixed Order, Shuffled Images, Label Stored)
# --------------------------------------------------
elif st.session_state.page == "image_tasks":
    st.header("D. Image Caption Tasks")

    all_images = [
        ("Relatable caption ideas", [
            "Taste-testing: the most important step in every masterpiece.",
            "Cooking is an art — tasting is quality control."
        ]),
        ("Playful caption ideas", [
            "When the champagne hits before the Roaring Twenties end.",
            "Pour decisions make the best memories."
        ]),
        ("Photographers with cameras captions", [
            "Smile! You’re making tomorrow’s headlines.",
            "Before smartphones, there were these warriors of the lens."
        ]),
        ("3D movie reaction captions", [
            "When 3D movies were too real.",
            "Immersive cinema before VR was even a dream."
        ]),
        ("Celebration caption ideas", [
            "When the bubble gun steals the show.",
            "POV: The party just hit its peak."
        ]),
        ("Inspirational caption ideas", [
            "Every trail leads to a story worth telling.",
            "Adventure begins at the edge of your comfort zone."
        ])
    ]

    if not st.session_state.image_condition_map:
        random.shuffle(all_images)
        image_pairs = [all_images[i:i+2] for i in range(0, 6, 2)]
        st.session_state.image_condition_map = [
            ("No-AI", image_pairs[0]),
            ("AI-first", image_pairs[1]),
            ("Human-first", image_pairs[2])
        ]

    img_round = st.session_state.image_round
    if img_round < 3:
        condition, image_pair = st.session_state.image_condition_map[img_round]
        st.subheader(f"Round {img_round + 1}: Condition = {condition}")

        base_key = condition.lower().replace("-", "_") + "_image_caption"
        captions_combined = []

        for name, ais in image_pair:
            st.markdown(f"### {name}")

            if condition == "No-AI":
                cap = st.text_area("Your caption:", key=f"{name}_text")
            elif condition == "AI-first":
                st.markdown("**Example AI Captions**")
                for c in ais:
                    st.write("-", c)
                cap = st.text_area("Your caption:", key=f"{name}_text")
            else:
                cap = st.text_area("Your caption:", key=f"{name}_text")
                if cap.strip():
                    st.markdown("### Example AI Captions")
                    for c in ais:
                        st.write("-", c)
                    improve_choice = st.radio("Would you like to revise your caption?",
                                              ["No", "Yes"], index=0, horizontal=True,
                                              key=f"{name}_improve")
                    revised_text = ""
                    if improve_choice == "Yes":
                        revised_text = st.text_area("Revise your caption below:", key=f"{name}_revised")
                    st.session_state.responses[f"{base_key}_improved"] = improve_choice
                    st.session_state.responses[f"{base_key}_revised"] = revised_text
            captions_combined.append(f"{name} — {cap}")

        st.session_state.responses[base_key] = " | ".join(captions_combined)

        if st.button("Next ➡️"):
            st.session_state.image_round += 1
            st.rerun()

    else:
        st.session_state.page = "post_reflection"
        st.rerun()

# --------------------------------------------------
# E. Final Reflection
# --------------------------------------------------
elif st.session_state.page == "post_reflection":
    st.header("🧩 Post-Survey Reflection")
    st.session_state.responses["overall_trust"] = st.slider(
        "Overall, I trusted the AI suggestions.", 1, 5, 3)
    st.session_state.responses["overall_original"] = st.slider(
        "Overall, my ideas felt original.", 1, 5, 3)
    st.session_state.responses["overall_fixation"] = st.slider(
        "It was hard to think beyond the AI’s ideas.", 1, 5, 3)

    if st.button("Finish Survey ✅"):
        st.session_state.responses["timestamp_end"] = datetime.now().isoformat()
        save_response(st.session_state.responses)
        st.session_state.page = "done"
        st.rerun()

# --------------------------------------------------
# F. End Page (GitHub Sync + Admin-only Download)
# --------------------------------------------------
elif st.session_state.page == "done":
    st.balloons()
    st.header("✅ Survey Complete")
    st.success("Thank you! Your responses have been saved and backed up.")

    file_path = "responses.csv"
    if os.path.exists(file_path):
        push_to_github(file_path)

    st.markdown("### 👩‍💼 Admin Access (Researcher Only)")
    admin_key = st.text_input("Enter admin passcode:", type="password")
    ADMIN_PASSWORD = "mySecretKey123"

    if admin_key == ADMIN_PASSWORD:
        st.success("🔐 Admin verified.")
        df = load_responses()
        if len(df) > 0:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download responses.csv",
                data=csv_data,
                file_name="responses.csv",
                mime="text/csv"
            )
        else:
            st.info("No responses recorded yet.")
    elif admin_key:
        st.error("❌ Incorrect passcode. Access denied.")
