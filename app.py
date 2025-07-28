import streamlit as st
from pathlib import Path
import google.generativeai as genai
#from api_key import api_key  # Make sure you have this file with your key
from gtts import gTTS
from deep_translator import GoogleTranslator
import os
import time
import glob
import re

try:
    api_key = st.secrets["api_keys"]["api_key"]
    #st.success("API key successfully loaded from secrets!")
    # Now you can use the 'api_key' variable
    # os.environ["YOUR_API_KEY_ENV_NAME"] = api_key # Optional: if a library needs it as an env var

except KeyError:
    st.error("API key not found. Please check your Streamlit secrets configuration.")
    st.stop()
# --- Page Configuration ---
st.set_page_config(
    page_title="AI Medical Doctor",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- CSS for modern styling and animations ---
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        /* --- General Body and Theme --- */
        body {
            font-family: 'Poppins', sans-serif;
            color: #FFFFFF; /* Set default text color to pure white */
        }

        /* --- Main App Container (Black Theme) --- */
        [data-testid="stAppViewContainer"] {
            background-color: #121212; /* Material Design Black */
            animation: fadeIn 1s ease-in-out;
        }
        
        /* --- Remove Header Bar --- */
        [data-testid="stHeader"] {
            background-color: transparent;
        }
        
        /* --- Markdown Text & Lists --- */
        [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
            color: #FFFFFF; /* Pure white for paragraphs AND list items */
            font-size: 1.05rem;
        }

        /* --- Main Content Padding --- */
        .main .block-container {
             padding-top: 2rem;
             padding-bottom: 2rem;
        }

        /* --- Titles and Headers --- */
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF; /* Pure white */
            font-weight: 600;
        }
        
        h1 {
            text-align: center;
        }

        h3 {
            border-bottom: 2px solid #10B981; /* Vibrant Green Accent */
            padding-bottom: 5px;
            margin-bottom: 1rem;
        }
        
        /* --- Sidebar Styling --- */
        [data-testid="stSidebar"] {
            background-color: #1E1E1E; /* Slightly lighter black for depth */
        }

        /* --- Button Styling --- */
        .stButton > button {
            width: 100%;
            border: 2px solid #10B981; /* Vibrant Green Accent */
            border-radius: 25px;
            color: #FFFFFF;
            background-color: transparent;
            padding: 12px 25px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease-in-out;
        }
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
            background-color: #10B981;
        }

        /* --- CSS for the Home Button Link --- */
        .home-button {
            display: block;
            width: 100%;
            padding: 12px 25px;
            background-color: transparent;
            color: #FFFFFF;
            text-align: center;
            border-radius: 25px;
            border: 2px solid #10B981; /* Vibrant Green Accent */
            text-decoration: none; /* Removes underline from link */
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease-in-out;
            box-sizing: border-box; /* Ensures padding doesn't break width */
            margin-bottom: 10px; /* Adds space between buttons */
        }
        .home-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
            background-color: #10B981;
            color: #FFFFFF;
            text-decoration: none;
        }

        /* --- File Uploader --- */
        [data-testid="stFileUploader"] {
            border: 2px dashed #10B981; /* Vibrant Green Accent */
            background-color: rgba(255, 255, 255, 0.05);
            padding: 1.5rem;
            border-radius: 10px;
        }
        [data-testid="stFileUploader"] label {
            color: #FFFFFF; /* Pure white */
            font-size: 1.1rem;
        }

        /* --- Selectbox (Dropdowns) --- */
        [data-testid="stSelectbox"] div {
            color: #000000; /* Pure white */
        }

        /* --- Image Caption Styling --- */
        .caption-text {
             text-align: center;
             font-style: italic;
             color: #A0AEC0; /* A slightly dimmer white for captions */
             margin-top: -10px;
        }

        /* --- Result/Diagnosis Section --- */
        .results-card {
            background-color: #1E1E1E; /* Slightly lighter black */
            padding: 1.5rem;
            border-radius: 10px;
            margin-top: 1.5rem;
            border-left: 5px solid #10B981; /* Vibrant Green Accent */
            animation: slideIn 0.7s ease-out;
        }

        /* --- Animations --- */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Management ---
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = None
if 'audio_file_path' not in st.session_state:
    st.session_state.audio_file_path = None
if 'uploaded_file_info' not in st.session_state:
    st.session_state.uploaded_file_info = None

# --- API and Model Configuration ---
try:
    genai.configure(api_key=api_key)
except (AttributeError, NameError):
    st.error("Please provide your API key in an `api_key.py` file.")
    st.stop()
    
os.makedirs("temp", exist_ok=True)

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
system_prompts = """As a highly skilled medical practitioner specializing in image analysis, you are tasked with examining medical images for a renowned hospital. Your expertise is crucial in identifying any anomalies, diseases, or health issues that may be present in the images.

Your Responsibilities include:
1. Detailed Analysis: Thoroughly analyze each image, focusing on identifying any abnormal findings.
2. Findings Report: Document all observed anomalies or signs of disease. Clearly articulate these findings in a structured format.
3. Recommendations and Next Steps: Based on your analysis, suggest potential next steps, including further tests or treatments as applicable.
4. Treatment Suggestions: If appropriate, recommend possible treatment options or interventions.

Important Notes:
1. Scope of Response: Only respond if the image pertains to human health issues.
2. Clarity of Image: In cases where the image quality impedes clear analysis, note that certain aspects are ‘Unable to be determined based on the provided image.’
3. Disclaimer: Accompany your analysis with the disclaimer: "Consult with a Doctor before making any decisions."
4. Your insights are invaluable in guiding clinical decisions. Please proceed with the analysis, adhering to the structured approach outlined above."""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# --- Helper Functions ---
def clean_up_old_files(days=7):
    """Removes MP3 files older than a specified number of days from the temp directory."""
    cutoff = time.time() - (days * 86400)
    for f in glob.glob("temp/*.mp3"):
        if os.stat(f).st_mtime < cutoff:
            os.remove(f)

def reset_app_state():
    """Clears the session state to reset the app."""
    st.session_state.ai_response = None
    st.session_state.audio_file_path = None
    st.session_state.uploaded_file_info = None
    # Rerunning is handled by Streamlit's on_click callback

# --- UI Layout ---
load_css()
clean_up_old_files(7) # Clean up old files on each run

# Sidebar
with st.sidebar:
    st.image("s3.png", width=100)
    st.header("Controls")
    
    # Add the Home/Reset button
    st.button("🏠 New Analysis", on_click=reset_app_state, use_container_width=True)
    st.markdown('<a href="https://ai-doctor-rho.vercel.app/" target="_self" class="home-button">🏠 Home</a>', unsafe_allow_html=True)
    st.markdown("---")
    # Language options
    languages = {
        "English": "en", "Hindi": "hi", "Bengali": "bn",
        "Korean": "ko", "Chinese": "zh-cn", "Japanese": "ja"
    }
    accents = {
        "Default": "com", "India": "co.in", "United Kingdom": "co.uk", "United States": "com",
        "Canada": "ca", "Australia": "com.au", "Ireland": "ie", "South Africa": "co.za"
    }

    out_lang = st.selectbox("Select output language", list(languages.keys()))
    english_accent = st.selectbox("Select English accent", list(accents.keys()), help="Select an accent for English text-to-speech.")
    
    output_language = languages[out_lang]
    tld = accents[english_accent]

# Main Page
st.title("AI Medical Doctor")
st.markdown("Upload a medical image to receive an AI-powered analysis and audio summary.")

# --- Main Logic ---
# The Uploader and Analyze button are now ALWAYS visible
uploaded_file = st.file_uploader(
    "Upload your medical image (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"]
)

if st.button("Analyze Image"):
    if uploaded_file:
        with st.spinner("Analyzing the image... Please wait. 🧠"):
            try:
                # Store file info in session state to display later
                st.session_state.uploaded_file_info = {
                    'data': uploaded_file.getvalue(),
                    'type': uploaded_file.type,
                    'caption': f"Analyzed Image: {uploaded_file.name}"
                }

                # Prepare for model
                image_data = st.session_state.uploaded_file_info['data']
                image_parts = [{"mime_type": st.session_state.uploaded_file_info['type'], "data": image_data}]
                prompt_parts = [image_parts[0], system_prompts]

                # Generate content
                response = model.generate_content(prompt_parts)
                ai_response = response.text.strip() if response.text else "No diagnosis could be generated."
                st.session_state.ai_response = ai_response

                # Translation and TTS
                translated_text = GoogleTranslator(source='en', target=output_language).translate(ai_response)
                
                safe_name = re.sub(r'[^A-Za-z0-9_\-]', '', ai_response[:20]) or "analysis_audio"
                file_path = f"temp/{safe_name}_{int(time.time())}.mp3"
                
                tts = gTTS(translated_text, lang=output_language, tld=tld, slow=False)
                tts.save(file_path)
                st.session_state.audio_file_path = file_path
                
                # We don't need to rerun anymore, as the result section will just appear
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload an image file first. 🖼️")

# --- Results Section ---
# Conditionally display results IF they exist in the session state
if st.session_state.ai_response:
    st.markdown("---")
    # Display the image that was analyzed
    st.image(
        st.session_state.uploaded_file_info['data'],
        width=250
    )
    st.markdown(f"<p class='caption-text'>{st.session_state.uploaded_file_info['caption']}</p>", unsafe_allow_html=True)
    
    # Display the diagnosis and audio in a card
    with st.container():
        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown("### 🔬 AI Diagnosis")
        st.markdown(st.session_state.ai_response) # Use st.markdown to render lists correctly
        
        if st.session_state.audio_file_path:
            st.markdown("### 🔊 Audio Summary")
            st.audio(st.session_state.audio_file_path, format="audio/mp3")
        st.markdown('</div>', unsafe_allow_html=True)