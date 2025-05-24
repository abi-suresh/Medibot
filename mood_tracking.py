import streamlit as st
import datetime
import pandas as pd

MOOD_OPTIONS = [
    ("😀", "Very Happy"),
    ("🙂", "Happy"),
    ("😐", "Neutral"),
    ("🙁", "Sad"),
    ("😢", "Very Sad"),
]

def log_mood():
    st.markdown("## 😊 Mood Tracker")
    today = datetime.date.today()

    if 'mood_history' not in st.session_state:
        st.session_state['mood_history'] = []

    emoji, label = zip(*MOOD_OPTIONS)
    mood = st.radio(
        "How are you feeling today?",
        options=range(len(MOOD_OPTIONS)),
        format_func=lambda x: f"{emoji[x]} {label[x]}"
    )

    note = st.text_input("Add a note (optional):")

    if st.button("Log Mood"):
        st.session_state['mood_history'].append({
            "date": today.strftime("%Y-%m-%d"),
            "mood": label[mood],
            "emoji": emoji[mood],
            "note": note
        })
        st.success("Mood logged!")

    if st.session_state['mood_history']:
        st.subheader("Mood History")
        df = pd.DataFrame(st.session_state['mood_history'])
        col1, col2 = st.columns([2, 3])
        with col1:
            st.dataframe(df)
        with col2:
            mood_map = {l: i for i, l in enumerate(label)}
            df['mood_score'] = df['mood'].map(mood_map)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            st.line_chart(df.set_index('date')['mood_score'])

        avg_score = df['mood_score'].mean()
        if avg_score >= 3:
            st.info("You seem to be feeling positive overall. Keep it up! 😊")
        elif avg_score <= 1:
            st.warning("You've been feeling low. Consider reaching out or using other mental health tools.")
        else:
            st.info("Your mood is fluctuating. Try to identify patterns or triggers in your notes.")
