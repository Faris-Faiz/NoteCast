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

def generate_summary(text, api_key):
    try:
        # Initialize the Gemini API with the user-provided API key
        genai.configure(api_key=api_key)

        # Set up the model (e.g., 'gemini-pro' for text generation)
        model = genai.GenerativeModel('gemini-pro')

        # Generate the summary
        response = model.generate_content(
            f"Summarize the following text while maintaining key points and academic integrity:\n\n{text}"
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
            f"You are a podcast script writer. Convert this summary into a natural, conversational dialogue between two speakers (Host and Expert). Include smooth transitions and maintain a casual yet informative tone.\n\nSummary:\n{summary}"
        )

        # Return the generated podcast script
        return response.text
    except Exception as e:
        st.error(f"Error generating podcast script: {str(e)}")
        return None

def synthesize_speech(text, voice_name):
    # Implement Piper TTS synthesis here
    # This is a placeholder - actual implementation will depend on Piper's API
    pass

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
    st.markdown("### 📝 Step 1: Upload Your Notes")
    uploaded_file = st.file_uploader(
        "Choose a PDF, DOCX, or image file",
        type=['pdf', 'docx', 'png', 'jpg', 'jpeg'],
        help="Supported formats: PDF, Word documents, and images (PNG, JPG)"
    )
    
    if uploaded_file is not None:
        # Create tabs for the conversion process
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Extracted Text", "📝 Summary", "🎭 Script", "🎧 Audio"])
        
        with tab1:
            st.markdown("### 📄 Step 2: Review Extracted Text")
            with st.spinner("Extracting text from your document..."):
                # Extract text based on file type
                file_type = uploaded_file.type
                if file_type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    text = extract_text_from_docx(uploaded_file)
                elif file_type.startswith("image/"):
                    text = extract_text_from_image(uploaded_file)
                
                st.text_area(
                    "Extracted Content",
                    text,
                    height=300,
                    help="Review the extracted text before generating the summary"
                )
                
                if st.button("Generate Summary", type="primary"):
                    if not gemini_api_key:
                        st.error("🔑 Please enter your Gemini API key in the sidebar first.")
                    else:
                        with st.spinner("🤖 AI is summarizing your content..."):
                            summary = generate_summary(text, gemini_api_key)
                            if summary:
                                st.session_state.current_summary = summary
                                st.success("✅ Summary generated successfully! Switch to the Summary tab.")
        
        with tab2:
            st.markdown("### 📝 Step 3: Review Summary")
            if st.session_state.current_summary:
                st.text_area(
                    "Generated Summary",
                    st.session_state.current_summary,
                    height=300,
                    help="Review the AI-generated summary"
                )
                
                if st.button("Create Podcast Script", type="primary"):
                    if not gemini_api_key:
                        st.error("🔑 Please enter your Gemini API key in the sidebar first.")
                    else:
                        with st.spinner("🤖 AI is creating your podcast script..."):
                            script = generate_podcast_script(st.session_state.current_summary, gemini_api_key)
                            if script:
                                st.session_state.current_script = script
                                st.success("✅ Podcast script created! Switch to the Script tab.")
            else:
                st.info("👈 Generate a summary from the Extracted Text tab first")
        
        with tab3:
            st.markdown("### 🎭 Step 4: Review Script")
            if st.session_state.current_script:
                st.text_area(
                    "Podcast Script",
                    st.session_state.current_script,
                    height=400,
                    help="Review the conversation script between Host and Expert"
                )
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    if st.button("Generate Audio", type="primary"):
                        with st.spinner("🎵 Generating podcast audio..."):
                            try:
                                audio_path = tts_engine.generate_podcast_audio(
                                    st.session_state.current_script,
                                    speaker1_voice,
                                    speaker2_voice
                                )
                                st.session_state.generated_audio_path = audio_path
                                st.success("✅ Audio generated! Switch to the Audio tab.")
                            except Exception as e:
                                st.error(f"❌ Error generating audio: {str(e)}")
            else:
                st.info("👈 Create a podcast script from the Summary tab first")
        
        with tab4:
            st.markdown("### 🎧 Step 5: Listen to Your Podcast")
            if st.session_state.generated_audio_path:
                st.audio(st.session_state.generated_audio_path)
                st.download_button(
                    "⬇️ Download Podcast",
                    data=open(st.session_state.generated_audio_path, 'rb'),
                    file_name="notecast_podcast.wav",
                    mime="audio/wav"
                )
            else:
                st.info("👈 Generate audio from the Script tab first")

if __name__ == "__main__":
    main()
