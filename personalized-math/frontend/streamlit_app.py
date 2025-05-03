import streamlit as st
import random
import numpy as np
import pickle
import pandas as pd
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.simulated_stream import EEGStreamer

# 📦 Load model
model = pickle.load(open("./backend/xgb_model.pkl", "rb"))

# 🧠 Initialize EEG streamer
streamer = EEGStreamer(path="./data/confusion_eeg.csv")

# 📘 Question bank
questions = {
    "easy": ["What is 7 + 3?", "Solve: 12 - 5", "2 x 4 = ?"],
    "medium": ["15 ÷ 3 = ?", "What is 3² + 1?", "Solve: (8 - 3) x 2"],
    "hard": ["What is √81 + 5?", "If x + 2 = 9, find x", "12 * (2 + 3) = ?"]
}

def get_question(level):
    return random.choice(questions[level])

# 🧠 App Title
st.title("🧠 BCI-Powered Math Tutor")

# 🔁 Session state init
if "confused_count" not in st.session_state:
    st.session_state.confused_count = 0
    st.session_state.total_count = 0

# 🔌 Get next EEG reading
eeg_input = streamer.get_next()
pred = model.predict(eeg_input)[0]  # 1 = confused, 0 = focused

# 💾 Track session stats
st.session_state.total_count += 1
if pred == 1:
    st.session_state.confused_count += 1

# 💡 Decide difficulty level
level = "easy" if pred == 1 else "hard"

# 🎯 Display current state and question
st.markdown(f"### Detected State: {'😵 Confused' if pred==1 else '🧠 Focused'}")
st.markdown(f"### Next Question Level: **{level.upper()}**")
st.markdown(get_question(level))

# 📊 Show EEG input features
st.write("EEG Features Used:")
st.dataframe(pd.DataFrame(eeg_input, columns=[
    'Theta', 'Alpha1', 'Alpha2', 'Beta1', 'Beta2', 'Gamma1', 'Gamma2'
]))

# 📈 Show confusion stats
confused_pct = 100 * st.session_state.confused_count / st.session_state.total_count
st.info(f"Session Confused Rate: {confused_pct:.2f}%")

# 🔁 Button to simulate next reading
if st.button("Next Question"):
    st.rerun()
