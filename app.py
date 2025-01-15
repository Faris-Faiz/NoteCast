import streamlit as st
import openai
import openrouter
from PIL import Image
import pytesseract
import PyPDF2
import docx
import io
import os
import json
import tempfile
from tts_utils import TTSEngine  # Import the TTSEngine
import google.generativeai as genai

# Configure page settings
st.set_page_config(
    page_title="NoteCast - Notes to Podcast Converter",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom styles
st.markdown("""
    <style>
        .main > div {
            padding: 2rem 3rem;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_summary' not in st.session_state:
    st.session_state.current_summary = ""
if 'generated_audio_path' not in st.session_state:
    st.session_state.generated_audio_path = None
if 'current_script' not in st.session_state:
    st.session_state.current_script = ""  # Add session state for the script

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_point_form_summary(text, api_key):
    try:
        # Initialize the Gemini API with the user-provided API key
        genai.configure(api_key=api_key)

        # Set up the model (e.g., 'gemini-pro' for text generation)
        model = genai.GenerativeModel('gemini-pro')

        # Generate the point-form summary
        response = model.generate_content(
            f"Provide a brief summary of the text followed by a concise point-form list of key points that can be used as study notes. Think deeply about your response:\n\n{text}"
        )

        # Return the generated summary
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def generate_podcast_script(summary, api_key):
    try:
        # Initialize the Gemini API with the user-provided API key
        genai.configure(api_key=api_key)

        # Set up the model (e.g., 'gemini-pro' for text generation)
        model = genai.GenerativeModel('gemini-pro')

        # Generate the podcast script
        response = model.generate_content(
            f"You are a podcast scriptwriter. Transform the provided summary into a natural, conversational dialogue between two speakers: Host and Expert. Use smooth transitions and maintain a casual yet informative tone. Incorporate engaging analogies and encourage the Host to make assumptions—some of which should be corrected by the Expert if wrong, and praised if correct. Ensure the conversation feels dynamic and relatable to the audience.\n\nSummary:\n{summary}"
        )

        # Return the generated podcast script
        return response.text
    except Exception as e:
        st.error(f"Error generating podcast script: {str(e)}")
        return None

def main():
    # Initialize TTS Engine
    tts_engine = TTSEngine()
    
    # Header
    st.title("NoteCast 🎙️")
    st.markdown("Transform your notes into engaging podcast conversations")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Configuration
        with st.expander("API Settings", expanded=True):
            gemini_api_key = st.text_input(
                "Gemini API Key",
                type="password",
                help="Enter your Gemini API key to enable AI features"
            )
        
        # Voice Configuration
        with st.expander("Voice Settings", expanded=True):
            st.markdown("##### Select voices for your podcast speakers")
            available_voices = tts_engine.get_available_voices()
            speaker1_voice = st.selectbox(
                "Host Voice",
                list(available_voices.keys()),
                help="Voice for the podcast host"
            )
            speaker2_voice = st.selectbox(
                "Expert Voice",
                list(available_voices.keys()),
                help="Voice for the expert guest"
            )

    # Check for missing voice models
    missing_models = tts_engine.check_voice_models()
    if missing_models:
        st.warning("⚠️ Some voice models are missing. Please check your installation.", icon="⚠️")
        with st.expander("Missing Models Details"):
            st.write(", ".join(missing_models))

    # Main content area
    st.markdown("### 📝 Step 1: Upload Your PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF file to generate a podcast"
    )
    
    if uploaded_file is not None:
        # Extract text from the PDF
        with st.spinner("Extracting text from your PDF..."):
            text = extract_text_from_pdf(uploaded_file)
        
        # Automatically generate point-form summary
        if gemini_api_key:
            with st.spinner("🤖 AI is summarizing your content..."):
                summary = generate_point_form_summary(text, gemini_api_key)
                if summary:
                    st.session_state.current_summary = summary
                    st.success("✅ Point-form summary generated successfully!")
        else:
            st.error("🔑 Please enter your Gemini API key in the sidebar first.")
        
        # Display the point-form summary
        if st.session_state.current_summary:
            st.markdown("### 📝 Point-Form Summary")
            st.text_area(
                "Generated Summary",
                st.session_state.current_summary,
                height=300,
                help="Review the AI-generated point-form summary"
            )
            
            # Generate podcast directly from the summary
            if st.button("Generate Podcast", type="primary"):
                if not gemini_api_key:
                    st.error("🔑 Please enter your Gemini API key in the sidebar first.")
                else:
                    with st.spinner("🤖 AI is creating your podcast..."):
                        script = generate_podcast_script(st.session_state.current_summary, gemini_api_key)
                        if script:
                            st.session_state.current_script = script  # Store the script in session state
                            with st.spinner("🎵 Generating podcast audio..."):
                                try:
                                    audio_path = tts_engine.generate_podcast_audio(
                                        script,
                                        speaker1_voice,
                                        speaker2_voice
                                    )
                                    st.session_state.generated_audio_path = audio_path
                                    st.success("✅ Podcast generated successfully!")
                                except Exception as e:
                                    st.error(f"❌ Error generating audio: {str(e)}")
        
        # Play and download the generated podcast
        if st.session_state.generated_audio_path:
            st.markdown("### 🎧 Step 2: Listen to Your Podcast")
            st.audio(st.session_state.generated_audio_path)

            # Add a dropdown to view the podcast script (above the download button)
            with st.expander("📜 View Podcast Script"):
                st.text_area(
                    "Podcast Script",
                    st.session_state.current_script,
                    height=400,
                    help="Review the conversation script between Host and Expert"
                )

            # Download button for the podcast
            st.download_button(
                "⬇️ Download Podcast",
                data=open(st.session_state.generated_audio_path, 'rb'),
                file_name="notecast_podcast.wav",
                mime="audio/wav"
            )

if __name__ == "__main__":
    main()