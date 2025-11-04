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
    """Append a participant's responses safely with quoting."""
    df_new = pd.DataFrame([data])
    file_path = "responses.csv"
    if os.path.exists(file_path):
        df_new.to_csv(file_path, mode="a", index=False, header=False,
                      encoding="utf-8", quoting=csv.QUOTE_ALL)
    else:
        df_new.to_csv(file_path, mode="w", index=False, header=True,
                      encoding="utf-8", quoting=csv.QUOTE_ALL)


def load_responses():
    """Safely load previous responses; auto-backup if file is malformed."""
    file_path = "responses.csv"
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            backup_name = f"responses_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(file_path, backup_name)
            st.warning(f"⚠️ responses.csv was inconsistent and backed up as {backup_name}. A new file has been created.")
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

    # Fixed round order: [No-AI, AI-first, Human-first]
    # Shuffle only which category (brief) appears in each
    if not st.session_state.condition_map:
        topics = random.sample(list(briefs.keys()), 3)
        conditions = ["No-AI", "AI-first", "Human-first"]
        st.session_state.condition_map = list(zip(conditions, topics))

    round_idx = st.session_state.text_round
    if round_idx < 3:
        condition, current_category = st.session_state.condition_map[round_idx]
        content = briefs[current_category]

        st.subheader(f"Round {round_idx + 1}: {current_category}")
        st.write("**Brief:**", content["brief"])
        user_key = f"{condition.lower().replace('-', '_')}_text"
        user_text = st.text_area("Write your headline:", key=f"text_{round_idx}")

        if condition == "AI-first":
            st.markdown("### Example AI Headlines")
            for h in content["ai"]:
                st.write("-", h)
        elif condition == "Human-first":
            st.markdown("_Write first, then see AI examples._")
            if user_text.strip():
                st.markdown("### Example AI Headlines")
                for h in content["ai"]:
                    st.write("-", h)

        st.session_state.responses[user_key] = user_text

        if user_text.strip() and st.button("Next ➡️"):
            st.session_state.text_round += 1
            st.rerun()

    else:
        st.session_state.page = "image_tasks"
        st.image_round = 0
        st.image_condition_map = []
        st.rerun()

# --------------------------------------------------
# D. Image Caption Tasks (Fixed Order, Shuffled Images)
# --------------------------------------------------
elif st.session_state.page == "image_tasks":
    st.header("D. Image Caption Tasks")

    all_images = [
        ("image1.jpg", "Relatable caption ideas", [
            "Taste-testing: the most important step in every masterpiece.",
            "Cooking is an art — tasting is quality control."
        ]),
        ("image2.jpg", "Playful caption ideas", [
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
        ("image5.jpg", "Celebration caption ideas", [
            "When the bubble gun steals the show.",
            "POV: The party just hit its peak."
        ]),
        ("image6.jpg", "Inspirational caption ideas", [
            "Every trail leads to a story worth telling.",
            "Adventure begins at the edge of your comfort zone."
        ])
    ]

    # Fixed order of rounds, shuffle image pairs only
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

        for img, name, ais in image_pair:
            st.markdown(f"### {name}")
            image_path = Path(__file__).parent / img
            if image_path.exists():
                st.image(str(image_path), caption=name)
            else:
                st.warning(f"⚠️ Could not find {img}.")

            cap = st.text_area("Write your caption:", key=f"{img}_text")

            if condition == "AI-first":
                st.markdown("**Example AI Captions**")
                for c in ais:
                    st.write("-", c)
            elif condition == "Human-first" and cap.strip():
                st.markdown("**Example AI Captions**")
                for c in ais:
                    st.write("-", c)

            st.session_state.responses[f"{condition.lower().replace('-', '_')}_{img}"] = cap

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
    st.markdown("Rate your overall experience across all text and image rounds (1–5):")
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
