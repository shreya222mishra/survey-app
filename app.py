import streamlit as st
import random, time, csv, os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="AI Creativity Survey", layout="wide")
st.title("🧠 AI Creativity and Idea Generation Survey")

# --------------------------------------------------
# Initialize session state
# --------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "intro"
if "condition" not in st.session_state:
    st.session_state.condition = random.choice(["AI-first","Human-first","No-AI"])
if "responses" not in st.session_state:
    st.session_state.responses = {}

# --------------------------------------------------
# Helper to write CSV
# --------------------------------------------------
def save_response(data):
    file_exists = os.path.isfile("responses.csv")
    with open("responses.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# --------------------------------------------------
# Helper to load responses for download
# --------------------------------------------------
def load_responses():
    if os.path.exists("responses.csv"):
        df = pd.read_csv("responses.csv")
        return df
    else:
        return pd.DataFrame()

# --------------------------------------------------
# Intro / Consent
# --------------------------------------------------
if st.session_state.page == "intro":
    st.markdown("""
    Welcome!  
    This study explores how people create text and image captions with or without AI help.  
    Your answers are anonymous. You may stop anytime.
    """)
    if st.button("Start Survey"):
        st.session_state.page = "demographics"
        st.rerun()

# --------------------------------------------------
# A. Participant description
# --------------------------------------------------
elif st.session_state.page == "demographics":
    st.header("A. Participant Information")
    pid = st.text_input("Participant ID (create any short code)")
    age = st.text_input("Age")
    gender = st.selectbox("Gender", ["Prefer not to say","Female","Male","Other"])
    major = st.text_input("Major or academic background")
    language = st.text_input("Native language (optional)")
    creative = st.text_area("Describe any prior creative work (writing, design, etc.)")
    if st.button("Next ➡️"):
        st.session_state.responses.update({
            "participant_id": pid, "age": age, "gender": gender,
            "major": major, "language": language, "creative_exp": creative,
            "condition": st.session_state.condition,
            "timestamp_start": datetime.now().isoformat()
        })
        st.session_state.page = "ai_familiarity"
        st.rerun()

# --------------------------------------------------
# B. AI Familiarity and Usage
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
    for q in qs:
        likerts[q] = st.slider(q,1,5,3)
    if st.button("Next ➡️"):
        st.session_state.responses.update(likerts)
        st.session_state.page = "text_tasks"
        st.rerun()

# --------------------------------------------------
# C. Text generation tasks
# --------------------------------------------------
elif st.session_state.page == "text_tasks":
    st.header("C. Text Generation: Write Headlines")
    briefs = {
        "Science & Technology": {
            "brief": "Researchers developed a new EV battery that charges in under five minutes, promising to revolutionize electric mobility.",
            "ai": [
                "Breakthrough Battery Promises Ultra-Fast EV Charging",
                "Game-Changer: EV Battery Cuts Charging Time to Minutes",
                "Rapid-Charge EV Battery Could Transform Electric Mobility",
                "University Team Unveils Lightning-Fast EV Battery Tech",
                "Automakers Eye 5-Minute Charge Battery for Future EVs",
                "Next-Gen EV Battery Slashes Charging Times, Boosts Adoption"
            ]
        },
        "Culture & Sports": {
            "brief": "A small rural town is hosting an international chess festival with players from 40 countries, bringing new life and pride to the community.",
            "ai": [
                "Global Chess Festival Brings New Life to Rural Town",
                "Quiet Town Turns Global Hub for Chess Enthusiasts",
                "From Silence to Strategy: Chess Festival Transforms Local Community",
                "Rural Town Welcomes the World for International Chess Event",
                "Checkmate to Obscurity: Chess Festival Revives Forgotten Town",
                "Cafés and Classrooms Become Arenas at Global Chess Festival"
            ]
        },
        "Health & Wellness": {
            "brief": "A new app claims it can detect stress by analyzing your voice. Developers say it can help track mental health in real time.",
            "ai": [
                "AI Listens for Stress: App Tracks Mental Health Through Speech",
                "Can Your Voice Reveal Stress? New AI App Says Yes",
                "Smartphone App Uses AI to Measure Stress in Real Time",
                "Talking Tech: AI Tool Gauges Stress from Voice Patterns",
                "AI App Promises Real-Time Stress Detection—Just by Listening",
                "Experts Weigh In on AI App That Detects Stress Through Speech"
            ]
        }
    }

    for topic,content in briefs.items():
        st.subheader(topic)
        st.write("**Brief:**", content["brief"])
        cond = st.session_state.condition
        user_key = f"{topic}_response"
        if cond=="AI-first":
            st.markdown("### Example AI Headlines")
            for h in content["ai"]:
                st.write("-",h)
            st.write("### Your Headlines")
            st.session_state.responses[user_key] = st.text_area(f"Write 3–5 headlines for {topic}")
        elif cond=="Human-first":
            user_text = st.text_area(f"Write 3–5 headlines for {topic}")
            st.markdown("### Example AI Headlines")
            for h in content["ai"]:
                st.write("-",h)
            st.session_state.responses[user_key] = user_text
        else: # No-AI
            st.session_state.responses[user_key] = st.text_area(f"Write 3–5 headlines for {topic}")

        st.markdown("Rate your experience (1–5):")
        st.session_state.responses[f"{topic}_trust"] = st.slider("I trusted the AI suggestions.",1,5,3)
        st.session_state.responses[f"{topic}_original"] = st.slider("My ideas felt original.",1,5,3)
        st.session_state.responses[f"{topic}_fixation"] = st.slider("It was hard to think beyond the AI’s ideas.",1,5,3)

    if st.button("Next ➡️"):
        st.session_state.page = "image_tasks"
        st.rerun()

# --------------------------------------------------
# D. Image generation (captions)
# --------------------------------------------------
elif st.session_state.page == "image_tasks":
    st.header("D. Image Caption Tasks")
    image_sets = [
        ("image_1.jpg","Cooking caption ideas",[
            "Taste-testing: the most important step in every masterpiece.",
            "Cooking is an art — tasting is quality control.",
            "When in doubt, taste it out."
        ]),
        ("image_2.jpg","1920s party scene captions",[
            "When the champagne hits before the Roaring Twenties end.",
            "Pour decisions make the best memories."
        ]),
        ("image_3.jpg","Photographers with cameras captions",[
            "Smile! You’re making tomorrow’s headlines.",
            "Before smartphones, there were these warriors of the lens."
        ]),
        ("image_4.jpg","3D movie reaction captions",[
            "When 3D movies were too real.",
            "Immersive cinema before VR was even a dream."
        ]),
        ("image_5.jpg","Bubble party captions",[
            "When the bubble gun steals the show.",
            "POV: The party just hit its peak."
        ]),
        ("image_6.jpg","Mountain hiking captions",[
            "Every trail leads to a story worth telling.",
            "Adventure begins at the edge of your comfort zone."
        ]),
        ("image_7.jpg","Brainstorming teamwork captions",[
            "Collaboration in action: where ideas come alive in color.",
            "Teamwork is the art of turning many thoughts into one vision."
        ])
    ]

    cond = st.session_state.condition
    for img,name,ais in image_sets:
        st.subheader(name)
        st.image(f"images/{img}", caption=f"{name} (placeholder)")
        if cond=="AI-first":
            st.markdown("### Example AI Captions")
            for c in ais: st.write("-",c)
            st.session_state.responses[f"{img}_caption"] = st.text_area("Write your own caption(s):")
        elif cond=="Human-first":
            cap = st.text_area("Write your own caption(s):")
            st.markdown("### Example AI Captions")
            for c in ais: st.write("-",c)
            st.session_state.responses[f"{img}_caption"] = cap
        else:
            st.session_state.responses[f"{img}_caption"] = st.text_area("Write your own caption(s):")

        st.session_state.responses[f"{img}_trust"] = st.slider("I trusted the AI suggestions.",1,5,3)
        st.session_state.responses[f"{img}_original"] = st.slider("My ideas felt original.",1,5,3)
        st.session_state.responses[f"{img}_fixation"] = st.slider("It was hard to think beyond the AI’s ideas.",1,5,3)

    if st.button("Finish Survey ✅"):
        st.session_state.responses["timestamp_end"] = datetime.now().isoformat()
        save_response(st.session_state.responses)
        st.session_state.page = "done"
        st.rerun()

# --------------------------------------------------
# End
# --------------------------------------------------
elif st.session_state.page == "done":
    st.balloons()
    st.header("✅ Survey Complete")
    st.success("Thank you! Your responses have been saved.")

    # Download section
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
