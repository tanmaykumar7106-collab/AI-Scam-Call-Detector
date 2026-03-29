* AI Scam Call Detector (Real-Time + Audio Analysis)

* Overview:-
	  The AI Scam Call Detector is a Python-based application designed to identify fraudulent phone calls in real-time or from recorded audio files. It uses speech recognition + rule-based NLP analysis to detect scam patterns such as OTP fraud, fake bank calls, KYC scams, and threat-based calls.
This project aims to improve digital safety by providing early warnings during suspicious calls.

* Problem Statement

Scam calls are increasing rapidly, targeting users with:-

1. OTP fraud
2. Fake bank verification
3. Lottery scams
4. Police/government threats

This system helps detect such scams by analyzing spoken language patterns and intent.

* Features

1. Real-time call detection using microphone
2. Recorded audio file analysis (.wav)
3. Multilingual support (English, Hindi, Telugu, Tamil, Malayalam)
4. Instant risk scoring system
5. Explainable detection (keyword + intent-based)
6. Lightweight (no heavy ML required)

* How It Works

o Step 1: Input
	Live voice from microphone  OR  Recorded audio file

o Step 2: Speech-to-Text
	Audio is converted into text using Google Speech Recognition API.

o Step 3: Text Analysis

The system checks:

1. Scam keywords (OTP, bank, KYC, etc.)
2. Authority pressure words (police, court)
3. Urgency phrases (urgent, immediately)


o Step 4: Risk Scoring

Each detected pattern increases a score:

Detection Type	          Score

1. Scam Keywords	   +2
2. Authority Words	   +3
3. Urgency Phrases         +2

o Step 5: Classification

1. SAFE -> Score < 4
2. SUSPICIOUS -> Score 4-6
3. FRAUD -> Score = 7

* Project Structure

 scam-call-detector/
 |
 |----app.py                # Main application file
 |----detector/
 |  |--engine.py            # Detection logic
 |  |--keywords.py          # Keyword datasets
 |
 |----audio/
    |--samples/             # Sample test files

