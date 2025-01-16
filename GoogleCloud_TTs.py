import os
from google.cloud import texttospeech

# Set the environment variable for service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "use api key GOOGLE_APPLICATION_CREDENTIALS"
print(f"Service account file exists: {os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))}")


def fetch_available_voices():
    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient()

    # Fetch all available voices
    voices = client.list_voices().voices
    available_voices = {}
    for voice in voices:
        gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
        for language_code in voice.language_codes:
            key = f"{voice.name} ({language_code}, {gender})"
            available_voices[key] = {
                "language_code": language_code,
                "voice_name": voice.name,
                "gender": gender,
            }
    return available_voices

# Google Cloud TTS Configuration
def synthesize_speech(text, output_file, language_code="en-US", voice_name="en-US-Wavenet-D"):
    client = texttospeech.TextToSpeechClient()

    # Set the text input
    input_text = texttospeech.SynthesisInput(text=text)

    # Configure the voice parameters
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )

    # Configure the audio file format
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Generate the speech
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    # Save the output to a file
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content written to {output_file}")

# Example usage
synthesize_speech("Hello, this is a test!", "output.wav")
if __name__ == "__main__":
    synthesize_speech("Hello, this is a test using Google Cloud TTS!", "test_output.wav")
