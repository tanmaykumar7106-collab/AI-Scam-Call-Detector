import os
import shutil
import tempfile
from collections import deque

import speech_recognition as sr
import streamlit as st
from pydub import AudioSegment

ffmpeg_path = shutil.which("ffmpeg")

if ffmpeg_path:
    AudioSegment.converter = ffmpeg_path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Scam Call Detector",
    page_icon="🛡️",
    layout="centered"
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    .status-safe {
        padding: 15px;
        border-radius: 10px;
        background-color: #ecfdf5;
        border: 1px solid #10b981;
        color: #065f46;
        font-weight: 600;
    }

    .status-suspicious {
        padding: 15px;
        border-radius: 10px;
        background-color: #fffbeb;
        border: 1px solid #f59e0b;
        color: #92400e;
        font-weight: 600;
    }

    .status-fraud {
        padding: 15px;
        border-radius: 10px;
        background-color: #fef2f2;
        border: 1px solid #ef4444;
        color: #991b1b;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SCAM DETECTOR
# ============================================================

class ScamCallDetector:

    def __init__(self):

        # ----------------------------------------------------
        # Scam-related keywords
        # ----------------------------------------------------

        self.scam_keywords = {

            "en-IN": {
                "otp",
                "bank",
                "account",
                "verify",
                "verification",
                "urgent",
                "police",
                "kbc",
                "lottery",
                "refund",
                "kyc",
                "suspend",
                "suspended",
                "arrest",
                "press",
                "password",
                "pin",
                "cvv",
                "credit card",
                "debit card",
                "transfer money",
                "send money",
                "reward",
                "prize",
                "winner",
                "click the link",
                "download app",
                "remote access",
                "anydesk",
                "teamviewer"
            },

            "hi-IN": {
                "ओटीपी",
                "बैंक",
                "खाता",
                "सत्यापित",
                "सत्यापन",
                "तत्काल",
                "पुलिस",
                "केबीसी",
                "लॉटरी",
                "रिफंड",
                "केवाईसी",
                "निलंबित",
                "गिरफ्तार",
                "दबाएं",
                "पासवर्ड",
                "पिन",
                "पैसे भेजें",
                "पैसे ट्रांसफर",
                "पुरस्कार"
            },

            "te-IN": {
                "ఓటిపి",
                "బ్యాంక్",
                "ఖాతా",
                "ధృవీకరించు",
                "తత్కాల",
                "పోలీస్",
                "కెబిసి",
                "లాటరీ",
                "రిఫండ్",
                "కెవైసి",
                "నిలిపివేయు",
                "అరెస్ట్",
                "ప్రెస్"
            },

            "ta-IN": {
                "ஓடிபி",
                "வங்கி",
                "கணக்கு",
                "சரிபார்க்க",
                "அவசரம்",
                "காவல்துறை",
                "கேபிசி",
                "லாட்டரி",
                "திரும்பப்பெறு",
                "கேவைசி",
                "நிறுத்து",
                "கைது",
                "அழுத்து"
            },

            "ml-IN": {
                "ഓടിപി",
                "ബാങ്ക്",
                "അക്കൗണ്ട്",
                "പരിശോധിക്കുക",
                "അടിയന്തരം",
                "പോലീസ്",
                "കെബിസി",
                "ലോട്ടറി",
                "റിഫണ്ട്",
                "കെവൈസി",
                "നിർത്തുക",
                "അറസ്റ്റ്",
                "അമർത്തുക"
            }
        }

        # ----------------------------------------------------
        # Authority impersonation words
        # ----------------------------------------------------

        self.authority_words = {

            "en-IN": {
                "police",
                "bank",
                "government",
                "court",
                "income tax",
                "rbi",
                "cyber crime",
                "customs"
            },

            "hi-IN": {
                "पुलिस",
                "बैंक",
                "सरकार",
                "कोर्ट",
                "आयकर",
                "आरबीआई"
            },

            "te-IN": {
                "పోలీస్",
                "బ్యాంక్",
                "ప్రభుత్వం",
                "కోర్ట్"
            },

            "ta-IN": {
                "காவல்துறை",
                "வங்கி",
                "அரசு",
                "நீதிமன்றம்"
            },

            "ml-IN": {
                "പോലീസ്",
                "ബാങ്ക്",
                "സർക്കാർ",
                "കോടതി"
            }
        }

        # ----------------------------------------------------
        # Urgency / pressure phrases
        # ----------------------------------------------------

        self.urgency_phrases = {

            "en-IN": {
                "urgent",
                "immediately",
                "right now",
                "as soon as possible",
                "within one hour",
                "last chance",
                "account will be blocked",
                "account will be suspended",
                "do not tell anyone"
            },

            "hi-IN": {
                "तत्काल",
                "तुरंत",
                "अभी",
                "जितनी जल्दी हो सके",
                "खाता बंद हो जाएगा",
                "किसी को मत बताना"
            },

            "te-IN": {
                "తత్కాల",
                "వెంటనే",
                "ఇప్పుడు",
                "వీలైనంత త్వరగా"
            },

            "ta-IN": {
                "அவசரம்",
                "உடனே",
                "இப்போது",
                "முடிந்தவரை விரைவாக"
            },

            "ml-IN": {
                "അടിയന്തരം",
                "ഉടനെ",
                "ഇപ്പോൾ",
                "സാധ്യമായത്ര വേഗം"
            }
        }

        self.current_score = 0
        self.detected_keywords = set()
        self.transcript_buffer = deque(maxlen=10)

        self.recognizer = sr.Recognizer()


    # ========================================================
    # RESET ANALYSIS
    # ========================================================

    def reset(self):

        self.current_score = 0
        self.detected_keywords.clear()
        self.transcript_buffer.clear()


    # ========================================================
    # CLASSIFY RISK
    # ========================================================

    def classify_risk(self):

        if self.current_score >= 10:
            return "FRAUD"

        if self.current_score >= 5:
            return "SUSPICIOUS"

        return "SAFE"


    # ========================================================
    # TEXT ANALYSIS
    # ========================================================

    def evaluate_text(self, text, language):

        text_lower = text.lower().strip()

        score = 0

        matched_keywords = []
        matched_authorities = []
        matched_urgencies = []

        keywords = self.scam_keywords.get(
            language,
            self.scam_keywords["en-IN"]
        )

        authorities = self.authority_words.get(
            language,
            self.authority_words["en-IN"]
        )

        urgencies = self.urgency_phrases.get(
            language,
            self.urgency_phrases["en-IN"]
        )


        # ----------------------------------------------------
        # Detect scam keywords
        # ----------------------------------------------------

        for keyword in keywords:

            if keyword.lower() in text_lower:

                matched_keywords.append(keyword)

                score += 2


        # ----------------------------------------------------
        # Detect authority impersonation
        # ----------------------------------------------------

        for word in authorities:

            if word.lower() in text_lower:

                matched_authorities.append(word)

                score += 3


        # ----------------------------------------------------
        # Detect urgency / pressure
        # ----------------------------------------------------

        for phrase in urgencies:

            if phrase.lower() in text_lower:

                matched_urgencies.append(phrase)

                score += 2


        # ----------------------------------------------------
        # Extra suspicious combinations
        # ----------------------------------------------------

        financial_terms = [
            "otp",
            "cvv",
            "pin",
            "password",
            "bank account",
            "credit card",
            "debit card"
        ]

        money_terms = [
            "send money",
            "transfer money",
            "payment",
            "pay now"
        ]

        if any(term in text_lower for term in financial_terms):
            score += 2

        if any(term in text_lower for term in money_terms):
            score += 3


        self.current_score = score

        classification = self.classify_risk()


        # ----------------------------------------------------
        # Risk percentage
        # This is a project risk indicator, not ML confidence.
        # ----------------------------------------------------

        risk_percentage = min(
            100,
            score * 8
        )


        return {

            "score": score,

            "risk_percentage": risk_percentage,

            "classification": classification,

            "keywords": sorted(
                set(matched_keywords)
            ),

            "authorities": sorted(
                set(matched_authorities)
            ),

            "urgencies": sorted(
                set(matched_urgencies)
            )
        }


    # ========================================================
    # SPEECH TO TEXT
    # ========================================================

    def transcribe_audio(
        self,
        audio_path,
        language
    ):

        with sr.AudioFile(audio_path) as source:

            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio_data = self.recognizer.record(
                source
            )

        try:

            transcript = self.recognizer.recognize_google(
                audio_data,
                language=language
            )

            return transcript

        except sr.UnknownValueError:

            raise ValueError(
                "Speech could not be understood. "
                "Please use clearer audio."
            )

        except sr.RequestError as error:

            raise RuntimeError(
                "Google Speech Recognition service could not "
                f"be reached: {error}"
            )


# ============================================================
# AUDIO FILE HANDLING
# ============================================================

MIME_EXTENSION_MAP = {

    "audio/wav": ".wav",

    "audio/x-wav": ".wav",

    "audio/mpeg": ".mp3",

    "audio/mp3": ".mp3",

    "audio/mp4": ".m4a",

    "audio/x-m4a": ".m4a",

    "audio/ogg": ".ogg",

    "application/ogg": ".ogg"
}


def get_audio_extension(audio_file):

    # --------------------------------------------------------
    # Try filename first
    # --------------------------------------------------------

    file_name = getattr(
        audio_file,
        "name",
        ""
    )

    if file_name:

        extension = os.path.splitext(
            file_name
        )[1].lower()

        if extension:
            return extension


    # --------------------------------------------------------
    # Fall back to MIME type
    # --------------------------------------------------------

    mime_type = getattr(
        audio_file,
        "type",
        ""
    )

    return MIME_EXTENSION_MAP.get(
        mime_type,
        ".wav"
    )


def save_audio_file(audio_file):

    extension = get_audio_extension(
        audio_file
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=extension
    ) as temporary_file:

        temporary_file.write(
            audio_file.getvalue()
        )

        return temporary_file.name


def convert_audio_to_wav(audio_file):

    """
    Converts MP3/MPEG/M4A/OGG audio into WAV.

    Browser microphone recordings and uploaded WAV files
    can be used directly without FFmpeg conversion.
    """

    input_path = save_audio_file(
        audio_file
    )

    extension = os.path.splitext(
        input_path
    )[1].lower()

    # --------------------------------------------------------
    # WAV needs no conversion
    # --------------------------------------------------------

    if extension == ".wav":

        return input_path


    output_path = input_path + ".wav"

    try:

        audio = AudioSegment.from_file(
            input_path
        )

        # Convert to mono
        audio = audio.set_channels(1)

        # Suitable speech-recognition sample rate
        audio = audio.set_frame_rate(
            16000
        )

        audio.export(
            output_path,
            format="wav"
        )

        return output_path

    except Exception as error:

        if os.path.exists(output_path):
            os.remove(output_path)

        raise RuntimeError(
            "Unable to convert the uploaded audio file. "
            "Make sure FFmpeg is installed. "
            f"Technical details: {error}"
        )

    finally:

        if os.path.exists(input_path):

            try:
                os.remove(input_path)

            except OSError:
                pass


# ============================================================
# LANGUAGE OPTIONS
# ============================================================

LANGUAGES = {

    "English": "en-IN",

    "Hindi": "hi-IN",

    "Telugu": "te-IN",

    "Tamil": "ta-IN",

    "Malayalam": "ml-IN"
}


# ============================================================
# SESSION STATE
# ============================================================

if "detector" not in st.session_state:

    st.session_state.detector = (
        ScamCallDetector()
    )


detector = st.session_state.detector


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        🛡️ AI Scam Call Detector
    </div>

    <div class="subtitle">
        Multilingual Scam Call Risk Analysis
    </div>
    """,
    unsafe_allow_html=True
)


st.write(
    """
    Analyze suspicious phone-call recordings using speech recognition
    and NLP-based rule analysis. The system searches for scam-related
    keywords, urgency tactics and possible authority impersonation.
    """
)


# ============================================================
# LANGUAGE SELECTION
# ============================================================

st.subheader(
    "1. Select Language"
)


selected_language = st.selectbox(

    "Language spoken in the call",

    list(
        LANGUAGES.keys()
    )
)


language_code = LANGUAGES[
    selected_language
]


# ============================================================
# AUDIO INPUT
# ============================================================

st.subheader(
    "2. Provide Call Audio"
)


input_method = st.radio(

    "Choose input method",

    [
        "Record using microphone",
        "Upload audio file"
    ],

    horizontal=True
)


audio_file = None


# ============================================================
# MICROPHONE MODE
# ============================================================

if input_method == "Record using microphone":

    st.write(
        "Record the suspicious call or a test sample."
    )

    audio_file = st.audio_input(
        "Record audio"
    )


# ============================================================
# FILE UPLOAD MODE
# ============================================================

else:

    audio_file = st.file_uploader(

        "Upload call recording",

        type=[
            "wav",
            "mp3",
            "mpeg",
            "m4a",
            "ogg"
        ],

        help=(
            "Supported formats: WAV, MP3, MPEG, "
            "M4A and OGG"
        )
    )


# ============================================================
# AUDIO PREVIEW
# ============================================================

if audio_file is not None:

    st.audio(
        audio_file
    )


# ============================================================
# ANALYSIS BUTTON
# ============================================================

if audio_file is not None:

    if st.button(
        "🔍 Analyze Call",
        type="primary",
        use_container_width=True
    ):

        detector.reset()

        temp_audio_path = None

        try:

            with st.spinner(
                "Processing audio..."
            ):

                # ------------------------------------------------
                # Convert file into WAV when required
                # ------------------------------------------------

                temp_audio_path = (
                    convert_audio_to_wav(
                        audio_file
                    )
                )


                # ------------------------------------------------
                # Speech to text
                # ------------------------------------------------

                transcript = detector.transcribe_audio(

                    temp_audio_path,

                    language_code
                )


                # ------------------------------------------------
                # Analyze transcript
                # ------------------------------------------------

                result = detector.evaluate_text(

                    transcript,

                    language_code
                )


            # ====================================================
            # RESULT
            # ====================================================

            st.divider()

            st.subheader(
                "Analysis Result"
            )


            # ----------------------------------------------------
            # Transcript
            # ----------------------------------------------------

            st.write(
                "**Transcript**"
            )

            st.info(
                transcript
            )


            # ----------------------------------------------------
            # Metrics
            # ----------------------------------------------------

            col1, col2, col3 = (
                st.columns(3)
            )


            with col1:

                st.metric(

                    "Risk Score",

                    result["score"]
                )


            with col2:

                st.metric(

                    "Risk Level",

                    result[
                        "classification"
                    ]
                )


            with col3:

                st.metric(

                    "Risk Indicator",

                    f'{result["risk_percentage"]}%'
                )


            # ----------------------------------------------------
            # Classification message
            # ----------------------------------------------------

            if (
                result["classification"]
                == "FRAUD"
            ):

                st.markdown(
                    """
                    <div class="status-fraud">
                    🚨 High-risk scam indicators detected.
                    Avoid sharing OTPs, passwords, PINs,
                    banking information or sending money.
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            elif (
                result["classification"]
                == "SUSPICIOUS"
            ):

                st.markdown(
                    """
                    <div class="status-suspicious">
                    ⚠️ Suspicious communication patterns
                    were detected. Verify the caller
                    independently before taking action.
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            else:

                st.markdown(
                    """
                    <div class="status-safe">
                    ✅ No strong scam indicators were
                    detected in this recording.
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ====================================================
            # DETECTED SIGNALS
            # ====================================================

            st.subheader(
                "Detected Warning Signals"
            )


            warning_found = False


            # ----------------------------------------------------
            # Scam keywords
            # ----------------------------------------------------

            if result["keywords"]:

                warning_found = True

                st.write(
                    "**Scam-related keywords**"
                )

                st.write(
                    ", ".join(
                        result["keywords"]
                    )
                )


            # ----------------------------------------------------
            # Authority impersonation
            # ----------------------------------------------------

            if result["authorities"]:

                warning_found = True

                st.write(
                    "**Authority-related terms**"
                )

                st.write(
                    ", ".join(
                        result["authorities"]
                    )
                )


            # ----------------------------------------------------
            # Urgency
            # ----------------------------------------------------

            if result["urgencies"]:

                warning_found = True

                st.write(
                    "**Urgency / pressure phrases**"
                )

                st.write(
                    ", ".join(
                        result["urgencies"]
                    )
                )


            if not warning_found:

                st.write(
                    "No predefined warning "
                    "signals were detected."
                )


        # ========================================================
        # ERROR HANDLING
        # ========================================================

        except ValueError as error:

            st.warning(
                str(error)
            )


        except RuntimeError as error:

            st.error(
                str(error)
            )


        except Exception as error:

            st.error(
                "Unexpected error while analyzing "
                f"the recording: {error}"
            )


        # ========================================================
        # TEMP FILE CLEANUP
        # ========================================================

        finally:

            if (
                temp_audio_path
                and os.path.exists(
                    temp_audio_path
                )
            ):

                try:

                    os.remove(
                        temp_audio_path
                    )

                except OSError:

                    pass


# ============================================================
# INFORMATION
# ============================================================

st.divider()


with st.expander(
    "How does the detector work?"
):

    st.write(
        """
        1. The uploaded or recorded audio is converted to WAV when required.
        2. Google Speech Recognition converts the call into text.
        3. The transcript is analyzed for suspicious words and phrases.
        4. Scam-related keywords increase the risk score.
        5. Authority impersonation and urgency tactics receive additional weight.
        6. The final score is classified as SAFE, SUSPICIOUS or FRAUD.
        """
    )


# ============================================================
# DISCLAIMER
# ============================================================

st.caption(
    """
    ⚠️ Experimental educational project. This application uses
    speech recognition and rule-based NLP analysis. The generated
    risk level is an indicator only and is not definitive proof
    that a caller is fraudulent.
    """
)