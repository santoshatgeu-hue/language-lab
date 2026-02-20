
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import azure.cognitiveservices.speech as speechsdk
import json
import pandas as pd
from datetime import datetime, date
import random



st.set_page_config(page_title="GEU Language Lab", layout="wide", page_icon="🏫")

# 1. Setup your Azure Credentials
AZURE_KEY = "2ms8Nj0zeuaQZiuAXKKiTn00jDUTsyJXHFom9aBXXtMb2gzummt0JQQJ99CBACGhslBXJ3w3AAAYACOGbUVv"
AZURE_REGION = "centralindia" # or your region


# --- 2. CURRICULUM & WARMUP BANK ---
curriculum = {
    "Placement Test": {
        "Level 1": ("Hello, how are you?", "नमस्ते, आप कैसे हैं?"),
        "Level 2": ("I am looking for a professional career in technology.", "मैं तकनीक में एक पेशेवर करियर की तलाश कर रहा हूं।"),
        "Level 3": ("Effective communication is the cornerstone of global business relations.", "प्रभावी संचार वैश्विक व्यापार संबंधों की आधारशिला है।")
    },
    "Hospitality": {
        "Check-in": ("Welcome to our hotel, may I see your ID?", "हमारे होटल में आपका स्वागत है, क्या मैं आपकी आईडी देख सकता हूँ?"),
        "Service": ("Would you like extra towels in your room?", "क्या आपको अपने कमरे में अतिरिक्त तौलिये चाहिए?")
    },
    "IT Support": {
        "Troubleshoot": ("Please check if the ethernet cable is plugged in properly.", "कृपया जाँचें कि क्या ईथरनेट केबल ठीक से प्लग की गई है।")
    },
    "Nursing": {
        "Vitals": ("I need to take your blood pressure and check your pulse.", "मुझे आपका रक्तचाप लेना है और आपकी नब्ज जांचनी है।")
    }
}

# New Expanded Vocabulary Bank
warmup_bank = [
    {"word": "Innovation", "options": ["सफलता (Success)", "नवाचार (New Ideas)", "चुनौती (Challenge)"], "answer": "नवाचार (New Ideas)"},
    {"word": "Persistent", "options": ["लगातार (Continuous)", "अस्थायी (Temporary)", "धीमा (Slow)"], "answer": "लगातार (Continuous)"},
    {"word": "Cornerstone", "options": ["छत (Roof)", "आधारशिला (Foundation)", "दीवार (Wall)"], "answer": "आधारशिला (Foundation)"},
    {"word": "Hospitality", "options": ["दुश्मनी (Enmity)", "सत्कार (Guest Welcome)", "परिवहन (Transport)"], "answer": "सत्कार (Guest Welcome)"},
    {"word": "Efficiency", "options": ["कार्यकुशलता (Work Ability)", "आलस (Laziness)", "शोर (Noise)"], "answer": "कार्यकुशलता (Work Ability)"}
]

# --- 3. SESSION STATE ---
if 'history' not in st.session_state: st.session_state.history = []
if 'last_lesson' not in st.session_state: st.session_state.last_lesson = ""
if 'user_level' not in st.session_state: st.session_state.user_level = "Not Tested"
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'last_practice_date' not in st.session_state: st.session_state.last_practice_date = None
if 'current_q' not in st.session_state: st.session_state.current_q = random.choice(warmup_bank)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🏫 Student Dashboard")
    st.markdown(f"### 🔥 Streak: **{st.session_state.streak} Days**")
    st.metric("Assessed Level", st.session_state.user_level)
    st.divider()
    st.subheader("🎯 Learning Goal")
    target_goal = st.slider("Target Accuracy %", 50, 100, 85)
    
    if st.session_state.history:
        latest_score = st.session_state.history[-1]['score']
        if latest_score >= target_goal: st.success(f"Goal Met! ({latest_score}%)")
        else: st.warning(f"Below Goal ({latest_score}%)")
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df['score'])
    
    if st.button("🗑️ Reset All Data"):
        st.session_state.clear()
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("🏫 GEU  Blended Learning Lab")
tab1, tab2 = st.tabs(["🎯 Placement & Practice", "🧩 Vocabulary Warmup"])

with tab1:
    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        mode = st.radio("Mode:", ["Placement", "Career Tracks"])
        if mode == "Placement":
            test_step = st.selectbox("Step:", list(curriculum["Placement Test"].keys()))
            target_text, hindi_text = curriculum["Placement Test"][test_step]
            current_key = f"placement_{test_step}"
        else:
            cat = st.selectbox("Track:", ["Hospitality", "IT Support", "Nursing"])
            les = st.selectbox("Lesson:", list(curriculum[cat].keys()))
            target_text, hindi_text = curriculum[cat][les]
            current_key = f"career_{les}"

    with col_info:
        st.markdown("### Practice Sentence")
        st.info(f"**English:** {target_text}")
        st.success(f"**Hindi:** {hindi_text}")

    if current_key != st.session_state.last_lesson:
        st.session_state.last_lesson = current_key
        if 'recorder' in st.session_state: del st.session_state['recorder']
        st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔊 Listen"):
            speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
            speech_config.speech_synthesis_voice_name = "en-IN-NeerjaNeural"
            speechsdk.SpeechSynthesizer(speech_config=speech_config).speak_text_async(target_text)
    with c2:
        audio = mic_recorder(start_prompt="🎤 Start Record", stop_prompt="🛑 Stop", key=f"rec_{current_key}")

# --- NEW VOCABULARY TAB LOGIC ---
with tab2:
    st.subheader("Vocabulary Warmup")
    q = st.session_state.current_q
    st.write(f"**What is the Hindi meaning of '{q['word']}'?**")
    
    choice = st.radio("Choose the correct option:", q['options'], key="vocab_radio")
    
    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("Check Answer"):
            if choice == q['answer']:
                st.success("✅ Correct!")
                st.balloons()
            else:
                st.error(f"❌ Incorrect. The answer is {q['answer']}.")
    with col_b:
        if st.button("Get New Word"):
            st.session_state.current_q = random.choice(warmup_bank)
            st.rerun()

# --- 6. ANALYSIS ENGINE ---
if audio:
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
    pron_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=target_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Word
    )
    push_stream = speechsdk.audio.PushAudioInputStream()
    push_stream.write(audio['bytes'])
    push_stream.close()
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=speechsdk.audio.AudioConfig(stream=push_stream))
    pron_config.apply_to(recognizer)
    
    with st.spinner("Analyzing..."):
        result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        res_json = json.loads(result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult))
        assessment = res_json['NBest'][0]['PronunciationAssessment']
        score = int(assessment['AccuracyScore'])
        
        # Streak Update
        today = date.today()
        if st.session_state.last_practice_date != today:
            st.session_state.streak += 1
            st.session_state.last_practice_date = today

        st.session_state.history.append({"lesson": current_key, "score": score, "time": datetime.now().strftime("%H:%M")})
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Accuracy", f"{score}%")
        m2.metric("Fluency", f"{int(assessment['FluencyScore'])}%")
        m3.metric("Completeness", f"{int(assessment['CompletenessScore'])}%")
        
        words = res_json['NBest'][0]['Words']
        feedback_html = "".join([f"<span style='color:{'#28a745' if w['PronunciationAssessment']['AccuracyScore'] > 75 else '#dc3545'}; font-size:28px; font-weight:bold; margin-right:12px;'>{w['Word']}</span>" for w in words])
        st.markdown(feedback_html, unsafe_allow_html=True)
