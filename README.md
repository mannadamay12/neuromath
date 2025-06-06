# NEUROMATH

NEUROMATH is a Human-Computer Interaction (HCI) project developed as part of NYU Spring 2025 coursework. It is an innovative adaptive learning platform that leverages Brain-Computer Interface (BCI) and eye-tracking technologies to personalize and optimize the learning experience for mathematical concepts. The project integrates EEG-based cognitive state monitoring, gaze tracking, and AI-powered content delivery to help learners master math topics more efficiently.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Components](#components)
    - [1. BCI Integration (epoc-lsl)](#1-bci-integration-epoc-lsl)
    - [2. Eye Tracking](#2-eye-tracking)
    - [3. AI-Powered Video Generation (manim-pipeline, manim-api)](#3-ai-powered-video-generation-manim-pipeline-manim-api)
    - [4. Adaptive Learning Web Platform](#4-adaptive-learning-web-platform)
    - [5. Personalized Math Notebooks](#5-personalized-math-notebooks)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Project Overview

NEUROMATH aims to create an adaptive educational environment that responds in real-time to the learner’s cognitive and attentional state. By combining EEG brainwave signals (using Emotiv EPOC X), eye-tracking data, and AI-driven educational video generation, NEUROMATH can:

- Detect when a learner is confused, disengaged, or attentive.
- Adapt the pace and style of educational video content accordingly.
- Provide feedback and session analytics to both learners and educators.

---

## Features

- **EEG-based Cognitive State Monitoring:** Uses Emotiv EPOC X and LSL streaming to capture brainwave patterns reflecting engagement, confusion, and attention.
- **Eye Tracking:** Monitors gaze and blinks for additional cues about focus and fatigue.
- **Adaptive Video Content:** Dynamically generates and delivers math educational videos using Manim, adjusting content based on real-time feedback.
- **Personalized Learning Analytics:** Tracks confusion triggers, session history, and cognitive status to tailor future learning.
- **Web-Based Dashboard:** Intuitive interface for monitoring BCI status, watching videos, and reviewing learning analytics.

---

## System Architecture

```
[EEG Headset] ----> [epoc-lsl (LSL Server)] ----> [Backend/Processing]
                                              
[Eye Tracker] ------> [main.py]                ↘
                                        [Adaptive Web Platform]
                                               |
                                   [AI Video Generator (Manim API/Pipeline)]
                                               |
                                      [Learner's Browser (index.html)]
```

---

## Components

### 1. BCI Integration (`epoc-lsl`)

- **Description:** Streams EEG data from Emotiv EPOC X headset via Lab Streaming Layer (LSL).
- **Dependencies:** `pipenv`, Python.
- **Usage:**
    ```bash
    pip install pipenv
    python -m pipenv install
    python -m pipenv run python main.py
    ```
    Use any LSL client (e.g., `bsl_stream_viewer`) or run example scripts to acquire or process EEG data.

### 2. Eye Tracking

- **Description:** Real-time gaze and blink detection using a webcam.
- **Usage:** Run `main.py` in the `eye-tracker` directory. Accepts command-line arguments for camera configuration.
- **Author:** [Alireza Bagheri](https://github.com/alireza787b/Python-Gaze-Face-Tracker)

### 3. AI-Powered Video Generation (`manim-pipeline`, `manim-api`)

- **Description:** Generates educational math videos with Manim and AI voiceover, based on learner needs.
- **API:** FastAPI backend to generate, store, and serve videos.
- **Requirements:** See `manim-pipeline/requirements.txt` for dependencies.
- **Usage:** Start the FastAPI server, use endpoints to request video generation, and review videos via the web platform.

### 4. Adaptive Learning Web Platform

- **Description:** The main user interface (`index.html`), displaying the video player, cognitive status, session analytics, and feedback forms.
- **Features:**
    - Real-time BCI connection status.
    - Video controls (play, restart, change speed).
    - Cognitive state visualization.
    - Session history and feedback submission.

### 5. Personalized Math Notebooks

- **Description:** Jupyter notebooks for EEG data analysis, prediction, and model training.
- **Example:** `personalized-math/notebooks/01_eeg_load_predict.ipynb` demonstrates EEG data loading and ML model saving.

---

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/mannadamay12/neuromath.git
    cd neuromath
    ```

2. **Set Up BCI Integration:**
    - Follow instructions in `epoc-lsl/README.md` to install dependencies and run the LSL server.

3. **Set Up Eye Tracker:**
    - Install dependencies and run `eye-tracker/main.py`.

4. **Set Up AI Video Pipeline:**
    - Install requirements in `manim-pipeline/requirements.txt`.
    - Start FastAPI server in `manim-api`.

5. **Launch Web Platform:**
    - Open `index.html` in your browser (ensure backend services are running and accessible).

---

## Usage

- **Connect the Emotiv EPOC X headset and start the LSL server.**
- **Run the eye-tracking script for gaze/blink monitoring.**
- **Access the web interface to watch adaptive math videos.**
- **Review session feedback and analytics to track learning progress.**

---

## Contributing

Contributions are welcome! Please fork the repo and submit a pull request, or open an issue for feature requests and bug reports.

---

## License

This project is for educational and research purposes. See individual component directories for licensing details and third-party acknowledgements.

---

## Acknowledgements

- [CyKit](https://github.com/CymatiCorp/CyKit) for Emotiv LSL server code
- [Alireza Bagheri](https://github.com/alireza787b/Python-Gaze-Face-Tracker) for gaze tracking
- [Manim Community](https://www.manim.community/) for video generation
- NYU HCI Spring 2025, all contributors, and the open-source community

---
