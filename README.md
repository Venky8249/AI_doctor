# AI Medical Doctor

An advanced web application that leverages Google's Generative AI to perform detailed analysis on medical images. This includes a modern, animated landing page and a powerful Streamlit-based tool for diagnosis, complete with multi-language text-to-speech summaries.

[![Landing Page](https://img.shields.io/badge/Live-Landing_Page-brightgreen?style=for-the-badge&logo=vercel)](https://ai-doctor-rho.vercel.app/)
[![Analyzer App](https://img.shields.io/badge/Live-Analyzer_App-blue?style=for-the-badge&logo=streamlit)](https://aidoctor-v.streamlit.app/)

---

## 🌟 Features

This project is composed of two main parts: a static landing page and the core Streamlit application.

### 📄 Landing Page (`index.html`)
- **Modern & Animated:** A fully responsive, visually appealing landing page built with Tailwind CSS.
- **Smooth Scroll Animations:** Dynamic animations that trigger as the user scrolls, creating an engaging experience.
- **Responsive Navigation:** A clean header that collapses into a hamburger menu on mobile devices.
- **Clear Call-to-Action:** Directs users to the main analysis application.

### 🩺 AI Analyzer (Streamlit App)
- **AI-Powered Diagnosis:** Upload a medical image (PNG, JPG) and receive a detailed, structured analysis from a powerful AI model.
- **Text-to-Speech Summaries:** Listen to the diagnosis in your preferred language.
- **Multi-Language & Accent Support:** Choose from several languages (English, Hindi, Bengali, etc.) and English accents for the audio output.
- **Sleek Dark Interface:** A custom-themed Streamlit interface that is easy on the eyes and simple to navigate.
- **Persistent Workflow:** Upload new images for analysis without needing to reset the entire page.

---

## 🛠️ Tech Stack

This project combines a modern front-end with a powerful Python backend.

- **Frontend (Landing Page):**
  - `HTML5`
  - `CSS3` with **Tailwind CSS** for styling
  - `JavaScript` for animations and interactivity

- **Backend & AI (Analyzer App):**
  - **Streamlit:** For creating the interactive web application interface.
  - **Python:** The core language for backend logic.
  - **Google Generative AI:** The AI model (`gemini-1.5-flash`) used for image analysis.
  - **gTTS (Google Text-to-Speech):** For converting the text diagnosis into audio.
  - **Deep Translator:** For translating the AI's response into different languages.

---

## 📂 Project Structure

The repository is organized into two main components:

```
/
├── index.html            # The main landing page.
├── streamlit_app.py      # The core Streamlit analysis tool.
├── api_key.py            # Stores the Google AI API key (should be in .gitignore).
├── temp/                 # Directory to temporarily store generated audio files.
└── README.md             # This file.
```

---

## 🚀 Setup and Installation (for the Streamlit App)

To run the AI Analyzer application on your local machine, follow these steps:

### Prerequisites
- Python 3.8 or higher
- A Google AI API Key

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Venky8249/AI_doctor.git
    cd AI_doctor
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install streamlit google-generativeai gTTS deep-translator
    ```

4.  **Create your API key file:**
    - Create a file named `api_key.py`.
    - Inside this file, add your Google AI API key like this:
      ```python
      api_key = "YOUR_GOOGLE_AI_API_KEY_HERE"
      ```

5.  **Run the Streamlit application:**
    ```bash
    streamlit run streamlit_app.py
    ```
    Your browser should automatically open to the application.

---

## 📖 Usage

1.  **Visit the Landing Page:** Open the `index.html` file or navigate to the live demo URL to learn about the project.
2.  **Launch the App:** Click on the "Launch App" or "Get Started Now" button.
3.  **Upload an Image:** In the Streamlit application, use the file uploader to select a medical image.
4.  **Select Options:** Choose your desired output language and accent from the sidebar.
5.  **Analyze:** Click the "Analyze Image" button.
6.  **View Results:** The AI-generated diagnosis will appear on the screen, along with an audio player to listen to the summary.

---

## ⚠️ Disclaimer

This tool is for **informational and educational purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified health provider with any questions you may have regarding a medical condition.
