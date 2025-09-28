"""
JalDoot Voice Service
Voice interaction capabilities for the groundwater assistant
"""

import os
import io
import base64
import tempfile
from typing import Optional, Dict, Any
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import pydub
from pydub import AudioSegment
import threading
import queue

class VoiceService:
    """Service for handling voice interactions"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
        except Exception as e:
            print(f"Warning: Microphone not available: {e}")
            self.microphone = None
        
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            self._configure_tts()
        except Exception as e:
            print(f"Warning: TTS engine not available: {e}")
            self.tts_engine = None
        
        # Audio processing settings
        self.audio_format = "wav"
        self.sample_rate = 44100
        self.channels = 1
        
        # Language settings
        self.supported_languages = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'hinglish': 'en-US'  # Use English recognition for Hinglish
        }
        
        # Audio queue for processing
        self.audio_queue = queue.Queue()
        self.is_processing = False
    
    def _configure_tts(self):
        """Configure text-to-speech engine settings"""
        try:
            # Set voice properties
            voices = self.tts_engine.getProperty('voices')
            
            # Try to find a suitable voice
            for voice in voices:
                if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level
            
        except Exception as e:
            print(f"TTS configuration error: {e}")
    
    def speech_to_text(self, audio_data: bytes, language: str = 'en') -> Dict[str, Any]:
        """Convert speech to text"""
        try:
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Load audio file
            audio = sr.AudioFile(temp_file_path)
            
            with audio as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Record audio
                audio_data = self.recognizer.record(source)
            
            # Recognize speech
            language_code = self.supported_languages.get(language, 'en-US')
            
            try:
                # Try Google Speech Recognition first
                text = self.recognizer.recognize_google(audio_data, language=language_code)
                confidence = 0.9  # Google doesn't provide confidence scores
                
            except sr.UnknownValueError:
                # Try with different language or fallback
                if language == 'hinglish':
                    text = self.recognizer.recognize_google(audio_data, language='en-US')
                    confidence = 0.7
                else:
                    raise
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return {
                'success': True,
                'text': text,
                'confidence': confidence,
                'language': language
            }
            
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'Could not understand audio',
                'text': '',
                'confidence': 0.0
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f'Speech recognition service error: {str(e)}',
                'text': '',
                'confidence': 0.0
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'text': '',
                'confidence': 0.0
            }
    
    def text_to_speech(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """Convert text to speech"""
        try:
            if language == 'hi':
                # Use Google TTS for Hindi
                return self._google_tts(text, 'hi')
            elif language == 'hinglish':
                # Use Google TTS for Hinglish (with English voice)
                return self._google_tts(text, 'en')
            else:
                # Use local TTS engine for English
                return self._local_tts(text)
                
        except Exception as e:
            return {
                'success': False,
                'error': f'TTS error: {str(e)}',
                'audio_data': None
            }
    
    def _local_tts(self, text: str) -> Dict[str, Any]:
        """Use local TTS engine"""
        try:
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            # Save speech to file
            self.tts_engine.save_to_file(text, temp_file_path)
            self.tts_engine.runAndWait()
            
            # Read audio data
            with open(temp_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return {
                'success': True,
                'audio_data': base64.b64encode(audio_data).decode(),
                'format': 'wav'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Local TTS error: {str(e)}',
                'audio_data': None
            }
    
    def _google_tts(self, text: str, language: str) -> Dict[str, Any]:
        """Use Google TTS"""
        try:
            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            # Save audio
            tts.save(temp_file_path)
            
            # Convert MP3 to WAV for better compatibility
            audio = AudioSegment.from_mp3(temp_file_path)
            wav_data = audio.export(format="wav").read()
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return {
                'success': True,
                'audio_data': base64.b64encode(wav_data).decode(),
                'format': 'wav'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Google TTS error: {str(e)}',
                'audio_data': None
            }
    
    def process_audio_file(self, file_path: str, language: str = 'en') -> Dict[str, Any]:
        """Process audio file and convert to text"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(file_path)
            
            # Convert to WAV format if needed
            if audio.frame_rate != self.sample_rate:
                audio = audio.set_frame_rate(self.sample_rate)
            
            if audio.channels != self.channels:
                audio = audio.set_channels(self.channels)
            
            # Export as WAV
            wav_data = audio.export(format="wav").read()
            
            # Convert to text
            result = self.speech_to_text(wav_data, language)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Audio processing error: {str(e)}',
                'text': '',
                'confidence': 0.0
            }
    
    def get_audio_info(self, audio_data: bytes) -> Dict[str, Any]:
        """Get information about audio data"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Load audio
            audio = AudioSegment.from_wav(temp_file_path)
            
            # Clean up
            os.unlink(temp_file_path)
            
            return {
                'duration': len(audio) / 1000.0,  # Duration in seconds
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'format': 'wav'
            }
            
        except Exception as e:
            return {
                'error': f'Could not analyze audio: {str(e)}'
            }
    
    def is_audio_available(self) -> bool:
        """Check if audio input/output is available"""
        try:
            # Check microphone
            mic_available = self.microphone is not None
            
            # Check TTS engine
            tts_available = self.tts_engine is not None
            
            return mic_available and tts_available
            
        except Exception:
            return False
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats"""
        return ['wav', 'mp3', 'm4a', 'flac', 'ogg']
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.tts_engine:
                self.tts_engine.stop()
        except Exception:
            pass
