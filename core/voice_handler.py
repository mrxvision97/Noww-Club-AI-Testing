try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
import threading
import queue
import io
import wave
from typing import Optional, Callable, Dict, Any
import streamlit as st
import time

class VoiceHandler:
    def __init__(self):
        """Initialize voice input/output handler"""
        self.available = SPEECH_RECOGNITION_AVAILABLE and TTS_AVAILABLE
        
        if self.available:
            try:
                # Initialize speech recognition
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Initialize text-to-speech
                self.tts_engine = pyttsx3.init()
                self._setup_tts()
                
                # Voice processing queue
                self.audio_queue = queue.Queue()
                self.is_listening = False
                self.recognition_callback = None
                
                # Calibrate microphone
                self._calibrate_microphone()
            except Exception as e:
                print(f"Voice handler initialization failed: {e}")
                self.available = False
        else:
            print("Voice capabilities not available - missing dependencies")
    
    def _setup_tts(self):
        """Setup text-to-speech engine"""
        try:
            # Set voice properties
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate (words per minute)
            self.tts_engine.setProperty('rate', 150)
            
            # Set volume (0.0 to 1.0)
            self.tts_engine.setProperty('volume', 0.8)
            
        except Exception as e:
            print(f"Error setting up TTS: {e}")
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Error calibrating microphone: {e}")
    
    def speak_text(self, text: str, async_mode: bool = True):
        """Convert text to speech"""
        if not self.available:
            print("Voice output not available")
            return
            
        try:
            if async_mode:
                # Run TTS in separate thread to avoid blocking
                threading.Thread(target=self._speak_sync, args=(text,), daemon=True).start()
            else:
                self._speak_sync(text)
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
    
    def _speak_sync(self, text: str):
        """Synchronous text-to-speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error in synchronous TTS: {e}")
    
    def start_listening(self, callback: Callable[[str], None] = None, timeout: int = 5):
        """Start listening for voice input"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.recognition_callback = callback
        
        # Start listening in separate thread
        threading.Thread(target=self._listen_continuously, args=(timeout,), daemon=True).start()
    
    def stop_listening(self):
        """Stop listening for voice input"""
        self.is_listening = False
    
    def _listen_continuously(self, timeout: int):
        """Continuously listen for voice input"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while self.is_listening:
                try:
                    with self.microphone as source:
                        # Listen for audio with timeout
                        audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                    
                    # Process audio in background
                    threading.Thread(target=self._process_audio, args=(audio,), daemon=True).start()
                    
                except sr.WaitTimeoutError:
                    # No speech detected within timeout
                    continue
                except Exception as e:
                    print(f"Error during listening: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Error in continuous listening: {e}")
        finally:
            self.is_listening = False
    
    def _process_audio(self, audio):
        """Process captured audio"""
        try:
            # Use Google's speech recognition
            text = self.recognizer.recognize_google(audio)
            
            if self.recognition_callback and text.strip():
                self.recognition_callback(text)
                
        except sr.UnknownValueError:
            # Speech was not clear enough
            pass
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
        except Exception as e:
            print(f"Error processing audio: {e}")
    
    def recognize_speech_from_audio(self, audio_data) -> Optional[str]:
        """Recognize speech from audio data"""
        try:
            # Convert audio data to speech
            text = self.recognizer.recognize_google(audio_data)
            return text.strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition: {e}")
            return None
        except Exception as e:
            print(f"Error recognizing speech: {e}")
            return None
    
    def record_audio(self, duration: int = 5):
        """Record audio for specified duration"""
        if not self.available:
            return None
            
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=duration)
                return audio
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            for voice in voices:
                voice_list.append({
                    'id': voice.id,
                    'name': voice.name,
                    'gender': 'female' if 'female' in voice.name.lower() else 'male'
                })
            return voice_list
        except Exception as e:
            print(f"Error getting voices: {e}")
            return []
    
    def set_voice(self, voice_id: str):
        """Set TTS voice by ID"""
        try:
            self.tts_engine.setProperty('voice', voice_id)
        except Exception as e:
            print(f"Error setting voice: {e}")
    
    def set_speech_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        try:
            self.tts_engine.setProperty('rate', max(50, min(300, rate)))
        except Exception as e:
            print(f"Error setting speech rate: {e}")
    
    def set_volume(self, volume: float):
        """Set TTS volume (0.0 to 1.0)"""
        try:
            self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
        except Exception as e:
            print(f"Error setting volume: {e}")
    
    def test_voice_output(self, test_text: str = "Hello, this is a test of the voice output system."):
        """Test voice output"""
        self.speak_text(test_text, async_mode=False)
    
    def test_voice_input(self, timeout: int = 5) -> Optional[str]:
        """Test voice input"""
        try:
            with self.microphone as source:
                st.info("🎤 Listening... Please speak now.")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
            text = self.recognizer.recognize_google(audio)
            return text
            
        except sr.WaitTimeoutError:
            return "No speech detected within timeout"
        except sr.UnknownValueError:
            return "Could not understand the speech"
        except sr.RequestError as e:
            return f"Error with speech recognition service: {e}"
        except Exception as e:
            return f"Error during voice input test: {e}"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get voice system information"""
        return {
            'microphone_available': self._test_microphone(),
            'tts_available': self._test_tts(),
            'available_voices': len(self.get_available_voices()),
            'current_rate': self.tts_engine.getProperty('rate'),
            'current_volume': self.tts_engine.getProperty('volume')
        }
    
    def _test_microphone(self) -> bool:
        """Test if microphone is available"""
        try:
            with self.microphone as source:
                pass
            return True
        except:
            return False
    
    def _test_tts(self) -> bool:
        """Test if TTS is available"""
        try:
            self.tts_engine.getProperty('voices')
            return True
        except:
            return False