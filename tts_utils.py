import os
import json
import tempfile
from datetime import datetime
import subprocess
import wave
import numpy as np
from config import (
    PIPER_VOICES,
    AUDIO_OUTPUT_DIR,
    SAMPLE_RATE,
    AUDIO_FORMAT
)

class TTSEngine:
    def __init__(self):
        self.voices = PIPER_VOICES
        self.output_dir = AUDIO_OUTPUT_DIR
        
    def _split_script_by_speakers(self, script):
        """Split the podcast script into segments by speaker."""
        segments = []
        current_speaker = None
        current_text = []
        
        for line in script.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for speaker indicators
            if line.startswith(('Host:', 'Expert:')):
                if current_speaker and current_text:
                    segments.append({
                        'speaker': current_speaker,
                        'text': ' '.join(current_text)
                    })
                current_speaker = line.split(':')[0].lower()
                current_text = [line.split(':', 1)[1].strip()]
            else:
                current_text.append(line)
        
        # Add the last segment
        if current_speaker and current_text:
            segments.append({
                'speaker': current_speaker,
                'text': ' '.join(current_text)
            })
            
        return segments

    def _synthesize_segment(self, text, voice_name):
        """Synthesize a single segment of text using Piper TTS."""
        try:
            voice_config = self.voices[voice_name]
            model_path = voice_config['model_path']
            
            # Create a temporary file for the text
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_text:
                temp_text.write(text)
                text_path = temp_text.name
            
            # Create a temporary file for the output audio
            with tempfile.NamedTemporaryFile(suffix=f'.{AUDIO_FORMAT}', delete=False) as temp_audio:
                output_path = temp_audio.name
            
            # Run Piper TTS command
            cmd = [
                'piper',
                '--model', model_path,
                '--output_file', output_path,
                '--text_file', text_path
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Clean up the temporary text file
            os.unlink(text_path)
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"Error running Piper TTS: {e.stderr}")
            raise
        except Exception as e:
            print(f"Error synthesizing speech: {str(e)}")
            raise

    def _combine_audio_files(self, audio_files):
        """Combine multiple audio files into a single file."""
        combined_path = os.path.join(
            self.output_dir,
            f"podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{AUDIO_FORMAT}"
        )
        
        # Read and combine all audio data
        combined_audio = []
        for audio_file in audio_files:
            with wave.open(audio_file, 'rb') as wf:
                audio_data = wf.readframes(wf.getnframes())
                combined_audio.append(audio_data)
        
        # Write combined audio to file
        with wave.open(combined_path, 'wb') as wf:
            wf.setnchannels(1)  # mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            for audio_data in combined_audio:
                wf.writeframes(audio_data)
        
        # Clean up temporary files
        for audio_file in audio_files:
            os.unlink(audio_file)
        
        return combined_path

    def generate_podcast_audio(self, script, host_voice, expert_voice):
        """Generate audio for the entire podcast script."""
        try:
            # Split script into segments
            segments = self._split_script_by_speakers(script)
            
            # Synthesize each segment
            audio_files = []
            for segment in segments:
                voice = host_voice if segment['speaker'] == 'host' else expert_voice
                audio_path = self._synthesize_segment(segment['text'], voice)
                audio_files.append(audio_path)
            
            # Combine all audio segments
            final_audio_path = self._combine_audio_files(audio_files)
            
            return final_audio_path
            
        except Exception as e:
            print(f"Error generating podcast audio: {str(e)}")
            raise

    def get_available_voices(self):
        """Return a list of available voices."""
        return {
            voice_id: {
                'name': config['name'],
                'language': config['language'],
                'gender': config['gender']
            }
            for voice_id, config in self.voices.items()
        }

    def check_voice_models(self):
        """Check if all required voice models are available."""
        missing_models = []
        for voice_id, config in self.voices.items():
            if not os.path.exists(config['model_path']):
                missing_models.append(voice_id)
        return missing_models
