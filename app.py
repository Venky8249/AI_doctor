import streamlit as st
from pathlib import Path
import google.generativeai as genai
from api_key import api_key
from gtts import gTTS
from deep_translator import GoogleTranslator
import os
import time
import glob
import re

# Configure GenAI
genai.configure(api_key=api_key)
os.makedirs("temp", exist_ok=True)

# Gemini config
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

# Initialize model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Streamlit UI
st.set_page_config(page_title="AI Doctor", page_icon=":robot:")
st.image("s3.png", width=150)
st.title("AI Doctor")
st.subheader("Analyze medical images & listen to AI diagnosis")

# Upload section
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

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
english_accent = st.selectbox("Select English accent", list(accents.keys()))

input_language = "en"
output_language = languages[out_lang]
tld = accents[english_accent]

# Button to handle image + analysis + TTS
if st.button("Analyze Image"):

    if uploaded_file:
        st.image(uploaded_file, width=200, caption="Uploaded Image")

        image_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": image_data}]
        prompt_parts = [image_parts[0], system_prompts]

        response = model.generate_content(prompt_parts)
        ai_response = response.text.strip() if response.text else "No diagnosis could be generated."

        # Translation and TTS
        translated_text = GoogleTranslator(source=input_language, target=output_language).translate(ai_response)
        safe_name = re.sub(r'[^A-Za-z0-9_\-]', '', ai_response[:20]) or "audio"
        file_path = f"temp/{safe_name}.mp3"
        tts = gTTS(translated_text, lang=output_language, tld=tld, slow=False)
        tts.save(file_path)

        # Display results
        st.markdown("### Diagnosis:")
        st.write(ai_response)

        #t.markdown("### Translated & Spoken Output:")
        #st.write(translated_text)
        st.audio(file_path, format="audio/mp3")

    else:
        st.warning("Please upload an image first.")

# Clean up old files
def remove_files_older_than(n_days):
    now = time.time()
    cutoff = now - (n_days * 86400)
    for f in glob.glob("temp/*.mp3"):
        if os.stat(f).st_mtime < cutoff:
            os.remove(f)

remove_files_older_than(7)
