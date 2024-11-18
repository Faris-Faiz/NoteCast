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

# Configure page settings
st.set_page_config(
    page_title="NoteCast - Notes to Podcast Converter",
    page_icon="🎙️",
    layout="wide"
)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_summary' not in st.session_state:
    st.session_state.current_summary = ""
if 'current_script' not in st.session_state:
    st.session_state.current_script = ""
if 'generated_audio_path' not in st.session_state:
    st.session_state.generated_audio_path = None

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_image(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

def generate_summary(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional content summarizer. Create a concise but comprehensive summary of the following text while maintaining key points and academic integrity."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def generate_podcast_script(summary):
    try:
        response = openrouter.ChatCompletion.create(
            model="gryphe/mythomax-l2-13b",
            messages=[
                {"role": "system", "content": "You are a podcast script writer. Convert this summary into a natural, conversational dialogue between two speakers (Host and Expert). Include smooth transitions and maintain a casual yet informative tone."},
                {"role": "user", "content": summary}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating podcast script: {str(e)}")
        return None

def synthesize_speech(text, voice_name):
    # Implement Piper TTS synthesis here
    # This is a placeholder - actual implementation will depend on Piper's API
    pass

def main():
    st.title("NoteCast - Transform Your Notes into Podcasts 🎙️")
    
    # Initialize TTS Engine
    tts_engine = TTSEngine()
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("Configuration")
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        openrouter_api_key = st.text_input("OpenRouter API Key", type="password")
        
        st.header("Voice Selection")
        available_voices = tts_engine.get_available_voices()
        speaker1_voice = st.selectbox("Select Host Voice", list(available_voices.keys()))
        speaker2_voice = st.selectbox("Select Expert Voice", list(available_voices.keys()))

    # Check for missing voice models
    missing_models = tts_engine.check_voice_models()
    if missing_models:
        st.warning(f"Missing voice models: {', '.join(missing_models)}")

    # Main content area
    uploaded_file = st.file_uploader("Upload your notes (PDF, DOCX, or Image)", type=['pdf', 'docx', 'png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        with st.spinner("Processing your file..."):
            # Extract text based on file type
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_text_from_docx(uploaded_file)
            elif file_type.startswith("image/"):
                text = extract_text_from_image(uploaded_file)
            
            st.text_area("Extracted Text", text, height=200)
            
            if st.button("Generate Summary"):
                if openai_api_key:
                    openai.api_key = openai_api_key
                    with st.spinner("Generating summary..."):
                        summary = generate_summary(text)
                        if summary:
                            st.session_state.current_summary = summary
                            st.text_area("Generated Summary", summary, height=200)
                else:
                    st.error("Please enter your OpenAI API key in the sidebar.")
            
            if st.session_state.current_summary and st.button("Generate Podcast Script"):
                if openrouter_api_key:
                    openrouter.api_key = openrouter_api_key
                    with st.spinner("Generating podcast script..."):
                        script = generate_podcast_script(st.session_state.current_summary)
                        if script:
                            st.session_state.current_script = script
                            st.text_area("Generated Podcast Script", script, height=300)
                else:
                    st.error("Please enter your OpenRouter API key in the sidebar.")
            
            if st.session_state.current_script and st.button("Generate Audio"):
                with st.spinner("Generating audio..."):
                    try:
                        audio_path = tts_engine.generate_podcast_audio(
                            st.session_state.current_script, 
                            speaker1_voice, 
                            speaker2_voice
                        )
                        st.session_state.generated_audio_path = audio_path
                        st.success("Audio generated successfully!")
                        st.audio(audio_path)
                    except Exception as e:
                        st.error(f"Error generating audio: {str(e)}")

if __name__ == "__main__":
    main()