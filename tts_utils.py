import os
from google.cloud import texttospeech
from config import AUDIO_OUTPUT_DIR


class TTSEngine:
    def __init__(self):
        self.voices = self._fetch_available_voices()

    def _fetch_available_voices(self):
        """Fetch all available voices from Google Cloud TTS."""
        client = texttospeech.TextToSpeechClient()
        response = client.list_voices()
        voices = {}

        for voice in response.voices:
            for language in voice.language_codes:
                key = f"{voice.name} ({language}, {voice.ssml_gender})"
                voices[key] = {
                    "language_code": language,
                    "voice_name": voice.name,
                    "gender": voice.ssml_gender,
                }
        return voices

    def get_available_voices(self):
        """Return all available voices."""
        return self.voices

    def generate_google_tts(self, text, output_file, voice_key):
        """Generate speech using Google Cloud TTS."""
        try:
            voice_config = self.voices[voice_key]
            client = texttospeech.TextToSpeechClient()

            # Set text input
            input_text = texttospeech.SynthesisInput(text=text)

            # Configure voice parameters
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_config["language_code"],
                name=voice_config["voice_name"],
            )

            # Configure audio output
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

            # Generate speech
            response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

            # Save to file
            with open(output_file, "wb") as out:
                out.write(response.audio_content)
                print(f"Audio content written to {output_file}")

        except Exception as e:
            print(f"Error generating TTS: {e}")
            raise

    def generate_podcast_audio(self, script, host_voice, expert_voice):
        """Generate podcast audio for both Host and Expert."""
        try:
            os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

            # Define audio file paths
            host_output = os.path.join(AUDIO_OUTPUT_DIR, "host_output.wav")
            expert_output = os.path.join(AUDIO_OUTPUT_DIR, "expert_output.wav")

            # Generate audio
            self.generate_google_tts(script, host_output, host_voice)
            self.generate_google_tts(script, expert_output, expert_voice)

            return host_output, expert_output

        except Exception as e:
            print(f"Error generating podcast audio: {e}")
            raise
